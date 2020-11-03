from fastapi import APIRouter, UploadFile, File
from typing import Optional, Set, List
from pydantic import BaseModel
from . import mongo
from datetime import datetime
import os, stat
import docker

client = docker.from_env()
router = APIRouter()
db = mongo.secure_code_platform
challenges = db.challenges
upload_path = '/api/solutions/'


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
    category_tags: List[str] = None
    author: str
    first_blood: str
    solutions_num: int
    wrong_solutions_num: int
    difficulty_tag: str
    difficulty_rating: int
    challenge_created: datetime
    challenge_modified: datetime


class WebChallenge(Challenge):
    image_name: str


@router.post('/list')
def get_challenges_list(tags: List[str] = None):
    if tags:
        challenges_list = challenges.find({'category_tags': {"$in": tags}}, {'_id': False})
        return {"challenges": list(challenges_list)}
    challenges_list = list(challenges.find({}, {'_id': False}))
    return {"challenges": challenges_list}


@router.put('/add_web_challenge')
async def add_web_challenge(challenge: WebChallenge):
    challenges.insert(challenge.dict(by_alias=True))
    return challenge


@router.get('/show_task')
def show_task():
    return {'pwd': list(os.listdir('api/challenges/web/example'))}


@router.post("/upload_solution/")
async def upload_solution(challenge_title: str, check: Optional[bool] = False, file: UploadFile = File(...)):
    timestamp = str(datetime.now().timestamp()).replace('.', '')
    filename = f"{timestamp}_{challenge_title.replace(' ', '_')}_{file.filename}"
    upload_file(filename, file)
    if check:
        result = await check_web_solution(filename, challenge_title)
        return {'result': result}
    return {"filename": filename}


def upload_file(filename, file):
    with open(upload_path + filename, 'wb') as f:
        [f.write(chunk) for chunk in iter(lambda: file.file.read(), b'')]
    return True


def get_challenge_answer():
    return 'Flag{checker_example_flag}'


def get_checker_image_name(challenge_name):
    return 'checker_example_server'


async def check_web_solution(filename, challenge_name):
    script = f'/solutions/{filename}'
    os.chmod(upload_path + filename, stat.S_IEXEC)
    solution_path = os.getenv('PWD') + upload_path
    server = client.containers.get(get_checker_image_name(challenge_name))
    server_ip = server.attrs['NetworkSettings']['Networks']['checkers-network']['IPAddress']
    container = client.containers.run(image='example_checker',
                                      auto_remove=True,
                                      volumes={solution_path: {'bind': '/solutions'}},
                                      detach=False,
                                      network='checkers-network',
                                      command=[script, f'http://{server_ip}:5000']
                                      )
    message = container.decode().strip()
    os.remove(upload_path + filename)
    if get_challenge_answer() == message:
        return True
    return False
