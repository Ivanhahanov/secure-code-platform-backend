import time

import requests
from pymongo import MongoClient
import random
import argparse
from itertools import cycle
from datetime import datetime, timezone
import os
import string

parser = argparse.ArgumentParser()
parser.add_argument("--create", action='store_true', help="create test data")
parser.add_argument("--remove", action='store_true', help="remove test data")
parser.add_argument("--count", type=int, help="count of tasks", default=20)
args = parser.parse_args()

mongo = MongoClient("mongodb",
                    username=os.getenv("MONGODB_USER"),
                    password=os.getenv("MONGODB_PASS"))
db = mongo.secure_code_platform

categories = []


def generate_random_pass(n):
    return ''.join([random.choice(string.ascii_letters) for _ in range(n)])


admin = {"username": "admin",
         "email": "admin@email.com",
         "full_name": "Admin",
         "disabled": False,
         "user_role": "user",
         "avatar_path": "",
         "password": generate_random_pass(8)}

user = {"username": "test",
        "email": "test@email.com",
        "full_name": "Test",
        "disabled": False,
        "user_role": "user",
        "password": generate_random_pass(8)}

challenges_categories = ['web', 'crypto', 'forensic', 'network', 'linux', 'reverse']
challenges_tags = []
challenges_difficult = ['easy', 'medium', 'hard', 'impossible']


def get_token():
    url = "http://api/users/token"
    data = {
        "username": user['username'],
        "password": user['password'],
    }
    r = requests.post(url, data)
    if r.status_code == 200:
        token = r.json().get('access_token')
        if token:
            return token
    print("Not valid arguments")
    exit(1)


def get_admin_token():
    url = "http://api/users/token"
    data = {
        "username": admin['username'],
        "password": admin['password'],
    }
    r = requests.post(url, data)
    if r.status_code == 200:
        token = r.json().get('access_token')
        if token:
            return token
    print("Not valid arguments")
    exit(1)


def generate_score():
    return random.choice(range(5, 255, 5))


def generate_data(data):
    for field in cycle(data):
        yield field


def generate_challenges():
    challenge = {
        "title": "Название Задание",
        "text": "*Задача организации*, _в особенности же начало повседневной работы_ по `формированию позиции` играет важную роль в формировании форм развития. Равным образом сложившаяся структура организации представляет собой интересный эксперимент проверки соответствующий условий активизации.",
        "tags": ["sql"],
        "author": "admin",
        "first_blood": None,
        "solutions_num": 0,
        "wrong_solutions_num": 0,
        "difficulty_rating": None,
        "challenge_modified": None,
        "flag": "$1mple_$ql_1nj3ct10n"}

    categories = generate_data(challenges_categories)
    difficulties = generate_data(challenges_difficult)
    challenges = [
        {
            "shortname": f"task{i}", **challenge,
            "category": next(categories),
            "difficulty_tag": next(difficulties),
            "score": generate_score(),
            "challenge_created": datetime.now(timezone.utc).isoformat(),
        } for i in range(args.count)
    ]
    return challenges


def generate_writeups(task_names: list):
    token = get_token()
    header = {
        "Authorization": f"Bearer {token}"}

    for shortname in task_names:
        writeup = {
            "challenge_shortname": shortname,
            "text": """
Разнообразный и богатый опыт рамки и место обучения кадров в значительной степени обуславливает создание модели развития. Таким образом постоянный количественный рост и сфера нашей активности требуют от нас анализа форм развития. 
* Пункт 1
* Пункт 2
* Пункт 3

Здесь какой-то код
```
bash -c
echo "hello world"
# комментарий
python3 run_script.py
```

ещё немного кода: `docker run --rm hello-world`
""",
        }
        url = f"http://api/writeup/new"
        r = requests.put(url, headers=header, json=writeup)
        if r.status_code != 200:
            print("Error:", r.json())
        score = {
            "challenge_shortname": shortname,
            "author": user['username'],
            "value": random.choice([1, -1]),
        }
        url = "http://api/writeup/score"
        r = requests.post(url, headers=header, json=score)
        if r.status_code != 200:
            print("Error:", r.json())
            return

    print("[+] add Writeups")
    print("[+] add Writeups scores")


def add_sponsors():
    token = get_admin_token()
    header = {
        "Authorization": f"Bearer {token}"}
    for i in range(args.count):
        sponsor = {
            "title": "Организация",
            "description": "Описание Организации",
        }
        image = {"sponsor_img": open('pt.png', 'rb')}
        url = "http://api/sponsors/add"
        r = requests.put(url, headers=header, params=sponsor, files=image)
        if r.status_code != 200:
            print("Error:", r.content)
            return
    print("[+] Add Sponsors")


def add_faq():
    token = get_admin_token()
    header = {
        "Authorization": f"Bearer {token}"}
    for i in range(args.count):
        sponsor = {
            "question": "Какой то вопрос?",
            "answer": "По своей сути рыбатекст является альтернативой традиционному lorem ipsum, который вызывает у некторых людей недоумение при попытках прочитать рыбу текст. В отличии от lorem ipsum, текст рыба на русском языке наполнит любой макет непонятным смыслом и придаст неповторимый колорит советских времен."
        }
        url = "http://api/faq/add"
        r = requests.put(url, headers=header, json=sponsor)
        if r.status_code != 200:
            print("Error:", r.content)
            return
    print("[+] Add Faq")


def create_user(user):
    r = requests.put("http://api/users/register", json=user).json()
    print(r)


def create_test_users():
    create_user(admin)
    print("[+] Admin created")
    print(admin['username'], admin['password'], sep=":")

    db.users.update({"username": "admin"}, {"$set": {"user_role": "admin"}})
    create_user(user)
    print("[+] User created")
    print(user['username'], user['password'], sep=":")


def remove_test_users():
    db.users.delete_one({"username": user["username"]})
    db.users.delete_one({"username": admin["username"]})


if args.create:
    time.sleep(2)
    create_test_users()
    challenges = generate_challenges()
    db.challenges.insert_many(challenges)
    print("[+] Add Challenges")
    generate_writeups([challenge['shortname'] for challenge in challenges])
    add_sponsors()
    add_faq()
    print(admin['username'], admin['password'])
    print(user['username'], user['password'])

elif args.remove:
    shortnames = [f"task{i}" for i in range(args.count)]
    db.challenges.delete_many({})
