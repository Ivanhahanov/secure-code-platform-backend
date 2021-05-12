from . import *
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()
challenges = db.challenges


class Flag(BaseModel):
    shortname: str
    flag: str


class Challenge(BaseModel):
    shortname: str = None
    flag: str = None
    score: int = None


class SubmittedUser(BaseModel):
    username: str
    solved_challenges_title: Dict[str, datetime] = {}
    num_of_solved_challenges: int = None
    place_in_scoreboard: int = None
    users_score: int = 0


@router.post('/submit_flag')
def submit_flag(flag: Flag, current_user: User = Depends(get_current_active_user)):
    if check_flag(**flag.dict()):
        add_score(current_user.username, flag.shortname)
        return {"flag": True}
    return {"flag": False}


def check_flag(flag, title):
    challenge = get_challenge(title)
    if challenge:
        if challenge.flag == flag:
            return True


def get_challenge(title):
    challenge = Challenge(**challenges.find_one({"title": title}))
    if all(challenge.dict().values()):
        return challenge


def add_score(username, challenge_title):
    user = SubmittedUser(**users.find_one({"username": username}))
    challenge = get_challenge(challenge_title)
    if not user.solved_challenges_title.get(challenge_title):
        user.solved_challenges_title[challenge_title] = datetime.now()
        user.users_score += challenge.score
        users.update_one({'username': username}, {'$set': user.dict(by_alias=True)})
