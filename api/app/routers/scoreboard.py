from fastapi import APIRouter
from . import *

router = APIRouter()


class ScoreboardUser(BaseModel):
    username: str
    users_score: int
    users_group: str = None
    num_of_solved_challenges: int
    place_in_scoreboard: int


@router.post('')
def scoreboard_info(_: User = Depends(get_current_active_user), page_number: int = 1, row_count: int = 10):
    sorted_users = get_sorted_users(page_number - 1, row_count)
    num_of_users = get_users_count()
    num_of_challenges = get_challenges_count()
    return {'num_of_users': num_of_users,
            'num_of_challenges': num_of_challenges,
            'scoreboard': sorted_users}


def get_sorted_users(page_count, row_count):
    users_list = list()
    skip = page_count * row_count
    limit = row_count
    users_slice = users.find({'user_role': {'$ne': 'admin'}}).sort(
        "users_score", 1
    ).skip(skip).limit(limit)
    for place, user in enumerate(users_slice, 1):
        user_info = ScoreboardUser(**user,
                                   num_of_solved_challenges=len(user.get("solved_challenges", [])),
                                   place_in_scoreboard=place + skip)
        users_list.append(user_info)
    return users_list


def get_users_count():
    users_count = users.find({'user_role': {'$ne': 'admin'}}).count()
    return users_count


def get_challenges_count():
    challenges_count = challenges.find().count()
    return challenges_count


def get_solved_challenges_count(username):
    return len(users.find_one({'username': username})['solved_challenges'])


def get_users_place(username):
    return users.find({"username": {"$lt": username, '$ne': 'admin'}}).sort(
        "users_score", 1
    ).count() + 1


def get_users_score(username):
    scoreboard_user = ScoreboardUser(**users.find_one({'username': username}))
    return scoreboard_user.users_score
