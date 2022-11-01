from fastapi import APIRouter, UploadFile, File
from . import *
from datetime import datetime
import os
import stat
import tarfile
import yaml

#
# client = docker.from_env()
router = APIRouter()
db = mongo.secure_code_platform
challenges = db.challenges
upload_path = '/api/solutions/'
upload_challenges_folder = '/api/challenges'
challenges_categories = ['web', 'crypto', 'forensic', 'network', 'linux', 'reverse']
challenges_tags = []
challenges_difficult = ['easy', 'medium', 'hard', 'impossible']


# solution_path = os.getenv('PWD') + upload_path

class ChallengeInfo(BaseModel):
    shortname: str
    title: str
    text: str
    score: int
    tags: List[str] = []
    category: str
    author: str
    first_blood: str = None
    solutions_num: int = 0
    wrong_solutions_num: int = 0
    difficulty_tag: str
    difficulty_rating: int = None
    challenge_created: datetime = None
    challenge_modified: datetime = None


class DBChallenge(ChallengeInfo):
    flag: str


class ShortChallenge(BaseModel):
    title: str
    shortname: str
    score: int
    tags: List[str]
    category: str
    author: str = None
    difficulty_tag: str
    challenge_created: datetime = None
    solved: bool


@router.post('/list')
def get_challenges_list(current_user: User = Depends(get_current_active_user),
                        difficult: Optional[list] = None,
                        tags: Optional[list] = None,
                        category: Optional[list] = None,
                        title: Optional[str] = None,
                        sort: Optional[str] = 'score',
                        sort_consistency: Optional[int] = 1,
                        page_count: int = 1, row_count: int = 10):
    sort_fields = ['score', 'date']
    if sort not in sort_fields:
        raise HTTPException(status_code=400, detail="invalid sort field")
    if sort_consistency not in (1, -1):
        raise HTTPException(status_code=400, detail="sort consistency value is not like 1 or -1")

    # define sort condition by score or date
    sort_condition = [(sort, sort_consistency)]
    if sort == 'date':
        sort_condition = [('challenge_created', sort_consistency)]

    # calculate skip and limit fields for database pagination
    skip = (page_count - 1) * row_count
    limit = row_count

    # load users solved challenges
    solved_challenges = users.find_one({'username': current_user.username}).get('solved_challenges', {})
    # define conditions for challenges search
    fields = {
        "difficulty_tag": {"$in": difficult},
        "tags": {"$in": tags},
        "category": {"$in": category}
    }
    # replace None fields to empty dict
    fields = [
        {k: v}
        if v["$in"]
        else {}
        for k, v in fields.items()
    ]
    # add text search to find conditions
    if title:
        fields.append({'title': {'$regex': title, '$options': 'i'}})

    # search by fields, sort by score and skip by pagecount
    challenges_slice = challenges.find(
        {"$and": fields}
    ).sort(
        sort_condition
    ).skip(skip).limit(limit)
    challenges_count = challenges.find({"$and": fields}).count()

    # fill challenges with solved flag
    short_challenges = []
    for challenge in challenges_slice:
        if challenge['shortname'] in solved_challenges.keys():
            short_challenges.append(ShortChallenge(**challenge, solved=True))
        else:
            short_challenges.append(ShortChallenge(**challenge, solved=False))
    return {"challenges": short_challenges,
            'num_of_challenges': challenges_count}


@router.get('/my_solved_challenges')
def my_solved_challenges(current_user: User = Depends(get_current_active_user),
                         page_number: int = 1, row_count: int = 10):
    solved_challenges = users_solved_challenges(current_user.username, page_number, row_count)
    count = len(users.find_one({'username': current_user.username}, {'solved_challenges': 1}).get('solved_challenges', []))
    return {"challenges": solved_challenges,
            "num_of_challenges": count}


def users_solved_challenges(username: str,
                            page_number: int = 1,
                            row_count: int = 10):
    solved_challenges_shortnames = users.find_one({'username': username}).get('solved_challenges')
    if not solved_challenges_shortnames:
        return []
    solved_short_challenges = [ShortChallenge(**challenges.find_one({'shortname': shortname}), solved=True)
                               for shortname in solved_challenges_shortnames]
    return solved_short_challenges[(page_number - 1) * row_count:page_number * row_count]


@router.get('/category_list')
def category_list(_: User = Depends(get_current_active_user)):
    return {"category_list": challenges.distinct('category')}


@router.get('/tags_list')
def tags_list(_: User = Depends(get_current_active_user)):
    return {"tags_list": challenges.distinct('tags')}


#
# @router.put('/add_container_challenge')
# async def add_container_challenge(challenge: ContainerChallenge,
#                                   current_user: User = Depends(get_current_user_if_editor)):
#     challenge = new_challenge_filter(challenge, current_user)
#     challenges.insert(challenge.dict(by_alias=True))
#     return challenge


# @router.put('/add_challenge')
# async def add_web_challenge(challenge: Challenge, current_user: User = Depends(get_current_user_if_editor)):
#     challenge = new_challenge_filter(challenge, current_user)
#     challenges.insert(challenge.dict(by_alias=True))
#     return challenge

@router.put('/add_challenge')
async def add_challenge(current_user: User = Depends(get_current_user_if_editor)):
    pass


# @router.put('/add_files_to_challenge')
# async def add_challenge_with_files(challenge_name: str,
#                                    public_file: UploadFile = File(...),
#                                    checkers_file: UploadFile = File(...),
#                                    _: User = Depends(get_current_user_if_editor)):
#     all_challenges_name = [challenge['title'] for challenge in challenges.find({}, {'_id': False})]
#     if challenge_name not in all_challenges_name:
#         raise HTTPException(status_code=400, detail='Invalid challenge name')
#     return {'challenge_name': challenge_name,
#             'public_filename': public_file.filename,
#             'checkers_file': checkers_file.filename}


# @router.get('/show_task')
# def show_task(current_user: User = Depends(get_current_active_user)):
#     return {'username': current_user.username, 'pwd': list(os.listdir('api/challenges/web/example'))}


@router.get('/get_challenge')
def get_challenges(shortname: str, current_user: User = Depends(get_current_active_user), text_format='html'):
    solved_challenges_list = users.find_one({'username': current_user.username}).get('solved_challenges')
    challenge = ChallengeInfo(**challenges.find_one({'shortname': shortname}))
    solved = False
    if solved_challenges_list:
        if challenge.shortname in solved_challenges_list.keys():
            solved = True
    if text_format == 'html':
        challenge.text = markdown_to_html(challenge.text)
    return {**challenge.dict(), "solved": solved}


@router.post('/upload_challenges')
def upload_challenges(archive: UploadFile = File(...), current_user: User = Depends(get_current_user_if_editor)):
    """
    :param archive: archive.tar with challenges
    :return: True if success
    """

    file_object = archive.file

    with tarfile.open(fileobj=file_object, mode='r') as tar:
        for name in tar.getnames():
            if name.endswith('.yml'):
                description_path = name
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tar, upload_challenges_folder)
    description = os.path.join(upload_challenges_folder, description_path)
    with open(description, 'r') as f:
        data = yaml.safe_load(f.read())
        result = add_description_to_database(data, current_user.username)
        if result is True:
            return {"result": True}
        return {"detail": f"Shortname {','.join(result)} already exists"}


def add_description_to_database(data, author):
    challenges_for_database = list()
    for shortname, values in data.items():
        print(shortname, values)
        challenge = DBChallenge(**values, shortname=shortname, author=author)
        if check_exists_shortname(challenge.shortname):
            challenges_for_database.append(challenge)

    if len(challenges_for_database) != len(data.keys()):
        return set(data.keys()).difference([value.shortname for value in challenges_for_database])

    for challenge in challenges_for_database:
        challenges.insert(challenge.dict())
    return True


def check_exists_shortname(shortname):
    if not list(challenges.find({"shortname": shortname})):
        return True


# @router.post("/upload_solution/")
# async def upload_solution(challenge_id: str, current_user: User = Depends(get_current_active_user),
#                           file: UploadFile = File(...)):
#     timestamp = str(datetime.now().timestamp()).replace('.', '')
#     filename = f"{timestamp}_{challenge_id}_{file.filename}"
#     upload_file(filename, file)
#     result, message = await check_container_solution(filename, challenge_id)
#     write_result_to_user_stat(current_user, challenge_id, result)
#     return {'username': current_user.username, 'result': result, 'detail': message}


def upload_file(filename, file):
    with open(upload_path + filename, 'wb') as f:
        [f.write(chunk) for chunk in iter(lambda: file.file.read(), b'')]
    return True


# async def check_container_solution(filename, challenge_id):
#     script = f'/solutions/{filename}'
#     os.chmod(upload_path + filename, stat.S_IEXEC)
#     challenge = ContainerChallenge(**challenges.find_one({'_id': ObjectId(challenge_id)}, {'_id': False}))
#     server = client.containers.get('test_' + challenge.image_name.split('/')[-1])
#     server_ip = server.attrs['NetworkSettings']['Networks']['checkers-network']['IPAddress']
#     try:
#         container = client.containers.run(image=challenge.checker_image_name,
#                                           auto_remove=True,
#                                           volumes={solution_path: {'bind': '/solutions'}},
#                                           detach=False,
#                                           network='checkers-network',
#                                           command=[script, f'http://{server_ip}:5000']
#                                           )
#     except docker.errors.ContainerError:
#         return False, 'Error in Container'
#     except docker.errors.ImageNotFound:
#         return False, 'Image Not Found'
#     except docker.errors.APIError:
#         return False, 'docker server return error'
#     finally:
#         os.remove(upload_path + filename)
#
#     message = container.decode().strip()
#     if get_challenge_flag(challenge_id) == message:
#         return True, 'Task Solved'
#     return False, 'Invalid Output'
#
#
# def write_result_to_user_stat(current_user, challenge_id, result):
#     user = UserScriptKiddy(**users.find_one({"username": current_user.username}, {'_id': False}))
#     challenge = ContainerChallenge(**challenges.find_one({"_id": ObjectId(challenge_id)}, {'_id': False}))
#     if result:
#         if not user.solved_challenges_id.get(challenge_id, None):
#             user.solved_challenges_id[challenge_id] = datetime.now()
#             user.users_score += challenge.score
#             users.update_one({'username': current_user.username}, {'$set': user.dict(by_alias=True)})


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
