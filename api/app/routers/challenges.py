from fastapi import APIRouter, UploadFile, File
from . import *
from datetime import datetime
import os
import stat
import docker

client = docker.from_env()
router = APIRouter()
db = mongo.secure_code_platform
upload_path = '/api/solutions/'
challenges_categories = ['web', 'crypto', 'forensic', 'network', 'linux', 'reverse']
challenges_tags = []
challenges_difficult = ['easy', 'medium', 'hard', 'impossible']
solution_path = os.getenv('PWD') + upload_path


class WriteUp(BaseModel):
    author: str
    text: str
    source_code_text: str
    writeup_created: datetime
    writeup_modified: datetime


class Challenge(BaseModel):
    title: str
    text: str
    input_example: str
    output_example: str
    score: int
    tags: List[str] = []
    category: str
    author: str = None
    first_blood: str = None
    solutions_num: int = 0
    wrong_solutions_num: int = 0
    difficulty_tag: str
    difficulty_rating: int = None
    challenge_created: datetime = None
    challenge_modified: datetime = None
    useful_resources: List[str] = []
    requirements: List[str] = []


class ContainerChallenge(Challenge):
    image_name: str
    checker_image_name: str
    flag: str


class ShortChallenge(BaseModel):
    title: str
    score: int
    tags: List[str]
    category: str
    author: str = None
    difficulty_tag: str
    challenge_created: datetime = None
    solved: bool


@router.post('/list')
def get_challenges_list(current_user: User = Depends(get_current_active_user)):
    short_challenges = []
    solved_challenges_id = users.find_one({'username': current_user.username})['solved_challenges_id']
    for challenge in challenges.find({}):
        if challenge['_id'] in set(map(ObjectId, solved_challenges_id)):
            short_challenges.append(ShortChallenge(**challenge, solved=True))
        else:
            short_challenges.append(ShortChallenge(**challenge, solved=True))
    return {'username': current_user.username, "challenges": short_challenges}


@router.post('/my_solved_challenges')
def my_solved_challenges(current_user: User = Depends(get_current_active_user)):
    solved_challenges_id = users.find_one({'username': current_user.username})['solved_challenges_id']
    solved_short_challenges = [ShortChallenge(**challenges.find_one({'_id': ObjectId(challenge_id)}), solved=True)
                               for challenge_id in solved_challenges_id]
    return solved_short_challenges


@router.get('/category_list')
def category_list(current_user: User = Depends(get_current_active_user)):
    return {'username': current_user.username, "category_list": challenges_categories}


@router.put('/add_container_challenge')
async def add_container_challenge(challenge: ContainerChallenge,
                                  current_user: User = Depends(get_current_user_if_editor)):
    challenge = new_challenge_filter(challenge, current_user)
    challenges.insert(challenge.dict(by_alias=True))
    return challenge


@router.put('/add_challenge')
async def add_web_challenge(challenge: Challenge, current_user: User = Depends(get_current_user_if_editor)):
    challenge = new_challenge_filter(challenge, current_user)
    challenges.insert(challenge.dict(by_alias=True))
    return challenge


@router.put('/add_files_to_challenge')
async def add_challenge_with_files(challenge_name: str,
                                   public_file: UploadFile = File(...),
                                   checkers_file: UploadFile = File(...),
                                   current_user: User = Depends(get_current_user_if_editor)):
    all_challenges_name = [challenge['title'] for challenge in challenges.find({}, {'_id': False})]
    if challenge_name not in all_challenges_name:
        raise HTTPException(status_code=400, detail='Invalid challenge name')
    return {'username': current_user.username,
            'challenge_name': challenge_name,
            'public_filename': public_file.filename,
            'checkers_file': checkers_file.filename}


@router.get('/show_task')
def show_task(current_user: User = Depends(get_current_active_user)):
    return {'username': current_user.username, 'pwd': list(os.listdir('api/challenges/web/example'))}


@router.get('/get_challenge')
def get_challenge_name(challenge_id: str, current_user: User = Depends(get_current_active_user)):
    challenge = Challenge(**challenges.find_one({'_id': ObjectId(challenge_id)}))
    return challenge


@router.post("/upload_solution/")
async def upload_solution(challenge_id: str, current_user: User = Depends(get_current_active_user),
                          file: UploadFile = File(...)):
    timestamp = str(datetime.now().timestamp()).replace('.', '')
    filename = f"{timestamp}_{challenge_id}_{file.filename}"
    upload_file(filename, file)
    result, message = await check_container_solution(filename, challenge_id)
    write_result_to_user_stat(current_user, challenge_id, result)
    return {'username': current_user.username, 'result': result, 'detail': message}


def upload_file(filename, file):
    with open(upload_path + filename, 'wb') as f:
        [f.write(chunk) for chunk in iter(lambda: file.file.read(), b'')]
    return True


async def check_container_solution(filename, challenge_id):
    script = f'/solutions/{filename}'
    os.chmod(upload_path + filename, stat.S_IEXEC)
    challenge = ContainerChallenge(**challenges.find_one({'_id': ObjectId(challenge_id)}, {'_id': False}))
    server = client.containers.get('test_' + challenge.image_name.split('/')[-1])
    server_ip = server.attrs['NetworkSettings']['Networks']['checkers-network']['IPAddress']
    try:
        container = client.containers.run(image=challenge.checker_image_name,
                                          auto_remove=True,
                                          volumes={solution_path: {'bind': '/solutions'}},
                                          detach=False,
                                          network='checkers-network',
                                          command=[script, f'http://{server_ip}:5000']
                                          )
    except docker.errors.ContainerError:
        return False, 'Error in Container'
    except docker.errors.ImageNotFound:
        return False, 'Image Not Found'
    except docker.errors.APIError:
        return False, 'docker server return error'
    finally:
        os.remove(upload_path + filename)

    message = container.decode().strip()
    if get_challenge_flag(challenge_id) == message:
        return True, 'Task Solved'
    return False, 'Invalid Output'


def write_result_to_user_stat(current_user, challenge_id, result):
    user = UserScriptKiddy(**users.find_one({"username": current_user.username}, {'_id': False}))
    challenge = ContainerChallenge(**challenges.find_one({"_id": ObjectId(challenge_id)}, {'_id': False}))
    if result:
        if not user.solved_challenges_id.get(challenge_id, None):
            user.solved_challenges_id[challenge_id] = datetime.now()
            user.users_score += challenge.score
            users.update_one({'username': current_user.username}, {'$set': user.dict(by_alias=True)})


def get_challenge_flag(challenge_id):
    return r.get(challenge_id).decode()


def new_challenge_filter(challenge, user):
    if set(challenge.category).issuperset(set(challenges_categories)):
        raise HTTPException(status_code=400, detail='Invalid Category')
    if challenge.difficulty_tag not in challenges_difficult:
        raise HTTPException(status_code=400, detail='Invalid Difficult Tag')
    challenge.author = user.username
    challenge.challenge_created = datetime.now()
    challenge.challenge_modified = datetime.now()
    return challenge
