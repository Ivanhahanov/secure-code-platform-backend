import requests
from pymongo import MongoClient
import random
import argparse
import pprint
from itertools import cycle
from datetime import datetime, timezone

parser = argparse.ArgumentParser()
parser.add_argument("--create", action='store_true', help="create test data")
parser.add_argument("--remove", action='store_true', help="remove test data")
parser.add_argument("--count", type=int, help="count of tasks", default=20)
parser.add_argument("-u", "--username", type=str, help="user with editor or admin credentials")
parser.add_argument("-p", "--password", type=str, help="users password")
parser.add_argument("-U", "--url", type=str, help="url of platform", default="localhost")

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


def generate_data(data):
    for field in cycle(data):
        yield field


def generate_challenges():
    challenge = {
        "title": "SQL приключения",
        "text": "Здесь могло бы быть описание, но админ слишком ленив. Реши таск и сдай флаг",
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
            "text": "test writeup in html format `some code`",
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

if args.create:
    challenges = generate_challenges()
    pprint.pprint(challenges)
    db.challenges.insert_many(challenges)
    if args.username and args.password and args.url:
        generate_writeups([challenge['shortname'] for challenge in challenges])


elif args.remove:
    shortnames = [f"task{i}" for i in range(args.count)]
    db.challenges.delete_many({"shortname": {"$in": shortnames}})
