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
    solved_challenges: Dict[str, str] = {}
    users_score: int = 0


@router.post('/submit_flag')
def submit_flag(flag: Flag, current_user: User = Depends(get_current_active_user)):
    if check_flag(**flag.dict()):
        add_score(current_user.username, flag.shortname)
        return {"flag": True}
    return {"flag": False}


def check_flag(flag, shortname):
    challenge = get_challenge(shortname)
    if challenge:
        if challenge.flag == flag:
            return True


def get_challenge(shortname):
    challenge = Challenge(**challenges.find_one({"shortname": shortname}))
    if all(challenge.dict().values()):
        return challenge


def add_score(username, challenge_title):
    user = SubmittedUser(**users.find_one({"username": username}))
    challenge = get_challenge(challenge_title)
    if not user.solved_challenges.get(challenge_title):
        user.solved_challenges[challenge_title] = datetime.now(timezone.utc).isoformat()
        user.users_score += challenge.score
        users.update_one({'username': username}, {'$set': user.dict(by_alias=True)})
