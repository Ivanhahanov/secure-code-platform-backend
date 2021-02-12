from fastapi import APIRouter
from . import *

router = APIRouter()


class ScoreboardUsers(BaseModel):
    username: str
    users_score: int = 0
    users_group: str = None
    place: int = None


class ScoreboardChallenges(BaseModel):
    title: str
    score: int
    category_tags: List[str]
    author: str = None
    first_blood: str = None
    difficulty_tag: str
    difficulty_rating: int = None


@router.post('/users')
def users_scoreboard(_: User = Depends(get_current_active_user), page_number: int = 1, row_count: int = 10):
    all_users = get_users_without_admin()
    scoreboard = sorted(all_users, key=lambda user: (user.users_score, user.username), reverse=True)
    for place, user in enumerate(scoreboard, 1):
        user.place = place
    return {'scoreboard': scoreboard[(page_number - 1) * row_count:page_number * row_count]}


@router.get('/num_of_users')
def get_num_of_users():
    num_of_users = users.count_documents({'user_role': {'$ne': 'admin'}})
    return {'num_of_users': num_of_users}


@router.get('/info')
def scoreboard_info(current_user: User = Depends(get_current_active_user)):
    all_users = get_users_without_admin()
    all_challenges = get_challenges()
    place = [i for i, user in enumerate(all_users) if user.username == current_user.username]
    if place == list():
        place = 0
    else:
        place = place[0] + 1
    return {'username': current_user.username,
            'num_of_users': len(all_users),
            'num_of_challenges': len(all_challenges),
            'users_score': get_users_score(current_user),
            'users_place': place}


def get_users_without_admin():
    all_users = [ScoreboardUsers(**user) for user in users.find({'user_role': {'$ne': 'admin'}})]
    return all_users


def get_challenges():
    all_challenges = [ScoreboardChallenges(**challenge) for challenge in challenges.find()]
    return all_challenges


def get_users_score(user):
    scoreboard_user = ScoreboardUsers(**users.find_one({'username': user.username}))
    return scoreboard_user.users_score
