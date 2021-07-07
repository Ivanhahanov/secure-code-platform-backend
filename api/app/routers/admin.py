from fastapi import APIRouter
from . import *

import string
import random


router = APIRouter()
db = mongo.secure_code_platform
challenges = db.challenges


class AdminPanelUser(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = False
    user_role: str = 'user'


# @router.get('/containers_list')
# def container_list(_: User = Depends(get_current_user_if_admin)):
#     return {'containers': [container.name for container in client.containers.list()]}


@router.get('/users')
def users_list(_: User = Depends(get_current_user_if_admin)):
    return {'users': [AdminPanelUser(**user) for user in db.users.find()]}


@router.get('/change_user_role')
def change_user_role(username: str, role: str, _: User = Depends(get_current_user_if_admin)):
    if role not in roles:
        raise HTTPException(status_code=400, detail="invalid Role")
    user = users.find_one_and_update({'username': username}, {'$set': {'user_role': role}}, {'_id': False})
    # TODO: get updated user
    if user is None:
        raise HTTPException(status_code=400, detail="invalid User")
    return {'changed': dict(user)}


# @router.post('/run_web_checkers_containers')
# def run_web_checkers_containers(challenge_id: str, _: User = Depends(get_current_user_if_admin)):
#     challenge = get_challenge(challenge_id)
#     r.set(challenge_id, generate_random_flag())
#     container_ip = run_web_container_with_flag(docker_image_name=challenge.image_name,
#                                                network='checkers-network',
#                                                flag=r.get(challenge_id).decode())
#     return {'container_ip': container_ip}


# @router.post('/run_web_containers')
# async def run_containers(challenge_id: str, _: User = Depends(get_current_user_if_admin)):
#     challenge = get_challenge(challenge_id)
#     container_ip = run_web_container_with_flag(docker_image_name=challenge.image_name,
#                                                network=None,
#                                                flag=challenge.flag,
#                                                ports={'5000/tcp': ('0.0.0.0', 5000)},
#                                                prod=True)
#     return {'container_ip': container_ip}


@router.get('/category/list')
def add_category():
    return {'categories': [Category(**category) for category in categories.find()]}


@router.put('/category/add')
def add_category(category: Category):
    try:
        result = categories.insert_one(category.dict(by_alias=True)).acknowledged
        return {"status": result, "category": category}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'DataBase Error: {e}')


@router.delete('/category/delete')
def add_category(category_name: str):
    try:
        result = categories.delete_one({"category_name": category_name}).acknowledged
        return {"status": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'DataBase Error: {e}')


@router.get('/tags/list')
def add_category():
    return {'tags': [Tag(**tag) for tag in tags.find()]}


@router.put('/tags/add')
def add_category(tag: Tag):
    try:
        result = tags.insert_one(tag.dict(by_alias=True)).acknowledged
        return {"status": result, "tag": tag}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'DataBase Error: {e}')


@router.delete('/tags/delete')
def add_category(tag_name):
    try:
        result = tags.delete_one({"tag_name": tag_name}).acknowledged
        return {"status": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'DataBase Error: {e}')


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