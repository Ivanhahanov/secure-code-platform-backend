from fastapi import APIRouter
from . import *

router = APIRouter()


@router.get('/users')
def users_scoreboard(current_user: User = Depends(get_current_active_user)):
    all_users = [UserScriptKiddy(**user) for user in users.find({}, {'user_role': False})]
    return {'username': current_user.username,
            'scoreboard': sorted(all_users, key=lambda user: (user.users_score, user.username), reverse=True)}
