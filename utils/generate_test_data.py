import requests
from pymongo import MongoClient
import random
import argparse
from itertools import cycle
from datetime import datetime, timezone

parser = argparse.ArgumentParser()
parser.add_argument("--create", action='store_true', help="create test data")
parser.add_argument("--remove", action='store_true', help="remove test data")
parser.add_argument("--count", type=int, help="count of tasks", default=20)
parser.add_argument("-u", "--username", type=str, help="user with editor or admin credentials", default="test")
parser.add_argument("-p", "--password", type=str, help="users password")
parser.add_argument("-U", "--url", type=str, help="url of platform", default="api")
parser.add_argument("-a", "--admin", type=str, help="user with editor or admin credentials", default="admin")
parser.add_argument("-P", "--admin_password", type=str, help="user with editor or admin credentials")
args = parser.parse_args()

mongo = MongoClient("mongodb",
                    username="root",
                    password="changeme")
db = mongo.secure_code_platform

categories = []

challenges_categories = ['web', 'crypto', 'forensic', 'network', 'linux', 'reverse']
challenges_tags = []
challenges_difficult = ['easy', 'medium', 'hard', 'impossible']


def get_token():
    url = f"http://{args.url}/users/token"
    data = {
        "username": args.username,
        "password": args.password,
    }
    r = requests.post(url, data)
    if r.status_code == 200:
        token = r.json().get('access_token')
        if token:
            return token
    print("Not valid arguments")
    exit(1)


def get_admin_token():
    url = f"http://{args.url}/users/token"
    data = {
        "username": args.admin,
        "password": args.admin_password,
    }
    r = requests.post(url, data)
    if r.status_code == 200:
        token = r.json().get('access_token')
        if token:
            return token
    print("Not valid arguments")
    exit(1)


def generate_data(data):
    for field in cycle(data):
        yield field


def generate_challenges():
    challenge = {
        "title": "Название Задание",
        "text": "*Задача организации*, _в особенности же начало повседневной работы_ по `формированию позиции` играет важную роль в формировании форм развития. Равным образом сложившаяся структура организации представляет собой интересный эксперимент проверки соответствующий условий активизации.",
        "score": 10,
        "tags": ["sql"],
        "author": "admin",
        "first_blood": None,
        "solutions_num": 0,
        "wrong_solutions_num": 0,
        "difficulty_rating": None,
        "challenge_created": datetime.now(timezone.utc).isoformat(),
        "challenge_modified": None,
        "useful_resources": ["https://owasp.org/www-community/attacks/SQL_Injection"],
        "flag": "$1mple_$ql_1nj3ct10n"}

    categories = generate_data(challenges_categories)
    difficulties = generate_data(challenges_difficult)
    challenges = [
        {
            "shortname": f"task{i}", **challenge,
            "category": next(categories),
            "difficulty_tag": next(difficulties)
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
        url = f"http://{args.url}/writeup/new"
        r = requests.put(url, headers=header, json=writeup)
        if r.status_code != 200:
            print("Error:", r.json())
        score = {
            "challenge_shortname": shortname,
            "author": args.username,
            "value": random.choice([1, -1]),
        }
        url = f"http://{args.url}/writeup/score"
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
        url = f"http://{args.url}/sponsors/add"
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
        url = f"http://{args.url}/faq/add"
        r = requests.put(url, headers=header, json=sponsor)
        if r.status_code != 200:
            print("Error:", r.content)
            return
    print("[+] Add Faq")

if args.create:
    challenges = generate_challenges()
    db.challenges.insert_many(challenges)
    print("[+] Add Challenges")
    if args.username and args.password and args.url:
        generate_writeups([challenge['shortname'] for challenge in challenges])
    if args.admin and args.admin_password and args.url:
        add_sponsors()
        add_faq()

elif args.remove:
    shortnames = [f"task{i}" for i in range(args.count)]
    db.challenges.delete_many({"shortname": {"$in": shortnames}})
