from fastapi import APIRouter, File, UploadFile
from typing import Optional
from . import *

router = APIRouter()


@router.get('/users')
def users_scoreboard(current_user: User = Depends(get_current_active_user)):
    all_users = [UserScriptKiddy(**user) for user in users.find({}, {'user_role': False})]
    return sorted(all_users, key=lambda user: (user.users_score, user.username), reverse=True)


