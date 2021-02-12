from fastapi import APIRouter
from . import *
from .challenges import ContainerChallenge
import docker
import string
import random

client = docker.from_env()

router = APIRouter()
db = mongo.secure_code_platform
challenges = db.challenges


@router.get('/containers_list')
def container_list(current_user: User = Depends(get_current_user_if_admin)):
    return {'user': current_user.username, 'role': current_user.user_role,
            'containers': [container.name for container in client.containers.list()]}


@router.get('/users')
def users_list(current_user: User = Depends(get_current_user_if_admin)):
    return {'username': current_user.username, 'users': list(db.users.find({}, {'_id': False}))}


@router.get('/change_user_role')
def change_user_role(username: str, role: str, current_user: User = Depends(get_current_user_if_admin)):
    if role not in roles:
        raise HTTPException(status_code=400, detail="invalid Role")
    user = users.find_one_and_update({'username': username}, {'$set': {'user_role': role}}, {'_id': False})
    # TODO: get updated user
    if user is None:
        raise HTTPException(status_code=400, detail="invalid User")
    return {'username': current_user.username, 'changed': dict(user)}


@router.post('/run_web_checkers_containers')
def run_web_checkers_containers(challenge_id: str, current_user: User = Depends(get_current_user_if_admin)):
    challenge = get_challenge(challenge_id)
    r.set(challenge_id, generate_random_flag())
    container_ip = run_web_container_with_flag(docker_image_name=challenge.image_name,
                                               network='checkers-network',
                                               flag=r.get(challenge_id).decode())
    return {'username': current_user.username, 'container_ip': container_ip}


@router.post('/run_web_containers')
async def run_containers(challenge_id: str, current_user: User = Depends(get_current_user_if_admin)):
    challenge = get_challenge(challenge_id)
    container_ip = run_web_container_with_flag(docker_image_name=challenge.image_name,
                                               network=None,
                                               flag=challenge.flag,
                                               ports={'5000/tcp': ('0.0.0.0', 5000)},
                                               prod=True)
    return {'username': current_user.username, 'container_ip': container_ip}


@router.get('/category/list')
def add_category():
    pass


@router.put('/category/add')
def add_category():
    pass


@router.post('/category/update')
def add_category():
    pass


@router.delete('/category/delete')
def add_category():
    pass


@router.get('/tags/list')
def add_category():
    pass


@router.put('/tags/add')
def add_category():
    pass


@router.post('/tags/update')
def add_category():
    pass


@router.delete('/tags/delete')
def add_category():
    pass


def generate_random_flag():
    symbols = string.digits + string.ascii_letters
    flag = ''.join(random.choice(symbols) for i in range(27))
    return 'Flag{%s}' % flag


def get_challenge(challenge_id):
    challenge = ContainerChallenge(**challenges.find_one({'_id': ObjectId(challenge_id)}, {'_id': False}))
    if not check_image(challenge.image_name):
        raise HTTPException(status_code=400, detail='Container not valid')
    return challenge


def check_image(image_name):
    return True


def get_container_ip(container_name, prod):
    container = client.containers.get(container_name)
    if prod:
        return container.attrs['NetworkSettings']['IPAddress']
    else:
        return container.attrs['NetworkSettings']['Networks']['checkers-network']['IPAddress']


def run_web_container_with_flag(docker_image_name, network, flag, ports=None, prod=False):
    if prod:
        container_name = docker_image_name.split('/')[-1]
    else:
        container_name = 'test_' + docker_image_name.split('/')[-1]
    client.containers.run(image=docker_image_name,
                          name=container_name,
                          auto_remove=True,
                          detach=True,
                          network=network,
                          ports=ports,
                          environment=[f'SCP_FLAG={flag}'],
                          )
    return get_container_ip(container_name, prod)
