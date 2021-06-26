from pymongo import MongoClient
import os
import argparse
import pprint
from itertools import cycle
from datetime import datetime, timezone
parser = argparse.ArgumentParser()
parser.add_argument("--create", action='store_true', help="create test data")
parser.add_argument("--remove", action='store_true', help="remove test data")
parser.add_argument("--count", type=int, help="remove test data", default=20)

args = parser.parse_args()

mongo = MongoClient("mongodb",
                    username=os.getenv("MONGODB_USER"),
                    password=os.getenv("MONGODB_PASS"))
db = mongo.secure_code_platform

categories = []

challenges_categories = ['web', 'crypto', 'forensic', 'network', 'linux', 'reverse']
challenges_tags = []
challenges_difficult = ['easy', 'medium', 'hard', 'impossible']


def generate_data(data):
    for field in cycle(data):
        yield field


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
if args.create:
    categories = generate_data(challenges_categories)
    difficulties = generate_data(challenges_difficult)
    challenges = [
        {
            "shortname": f"task{i}", **challenge,
            "category": next(categories),
            "difficulty_tag": next(difficulties)
        } for i in range(args.count)
    ]
    pprint.pprint(challenges)
    db.challenges.insert_many(challenges)
elif args.remove:
    shortnames = [f"task{i}" for i in range(args.count)]
    db.challenges.delete_many({"shortname": {"$in": shortnames}})
