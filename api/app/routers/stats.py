# TODO: stats for prometheus
from fastapi import APIRouter
from . import *

router = APIRouter()


@router.get('/')
def stats(_: User = Depends(get_current_active_user)):
    return {'num_of_users': db.users.find({'user_role': {'$ne': 'admin'}}).count(),
            'num_of_challenges': db.challenges.find().count()}
