from fastapi import APIRouter, UploadFile, File
from typing import List
from . import *
from datetime import datetime
import os
import stat
import docker

client = docker.from_env()
router = APIRouter()
db = mongo.secure_code_platform
challenges = db.challenges
upload_path = '/api/solutions/'
challenges_categories = ['web', 'crypto', 'forensic', 'network', 'linux', 'reverse']
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
    category_tags: List[str]
    author: str = None
    first_blood: str = None
    solutions_num: int = 0
    wrong_solutions_num: int = 0
    difficulty_tag: str
    difficulty_rating: int = None
    challenge_created: datetime
    challenge_modified: datetime


class ContainerChallenge(Challenge):
    image_name: str
    checker_image_name: str


@router.post('/list')
def get_challenges_list(current_user: User = Depends(get_current_active_user), tags: List[str] = None):
    if tags:
        challenges_list = challenges.find({'category_tags': {"$in": tags}}, {'_id': False})
        return {"challenges": list(challenges_list)}
    challenges_list = list(challenges.find({}, {'_id': False}))
    return {'username': current_user.username, "challenges": challenges_list}


@router.post('/category_list')
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


@router.post("/upload_solution/")
async def upload_solution(challenge_title: str, current_user: User = Depends(get_current_active_user),
                          file: UploadFile = File(...)):
    timestamp = str(datetime.now().timestamp()).replace('.', '')
    filename = f"{timestamp}_{challenge_title.replace(' ', '_')}_{file.filename}"
    upload_file(filename, file)
    result, message = await check_container_solution(filename, challenge_title)
    return {'username': current_user.username, 'result': result, 'message': message}


def upload_file(filename, file):
    with open(upload_path + filename, 'wb') as f:
        [f.write(chunk) for chunk in iter(lambda: file.file.read(), b'')]
    return True


async def check_container_solution(filename, challenge_name):
    script = f'/solutions/{filename}'
    os.chmod(upload_path + filename, stat.S_IEXEC)
    challenge = ContainerChallenge(**challenges.find_one({'title': challenge_name}, {'_id': False}))
    server = client.containers.get('checker_' + challenge.image_name)
    server_ip = server.attrs['NetworkSettings']['Networks']['checkers-network']['IPAddress']
    try:
        container = client.containers.run(image='example_checker',
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
    if challenge.output_example == message:
        return True, 'Task Solved'
    return False, 'Invalid Output'


def new_challenge_filter(challenge, user):
    if set(challenge.category_tags).issuperset(set(challenges_categories)):
        raise HTTPException(status_code=400, detail='Invalid Category')
    if challenge.difficulty_tag not in challenges_difficult:
        raise HTTPException(status_code=400, detail='Invalid Difficult Tag')
    challenge.author = user.username
    return challenge
