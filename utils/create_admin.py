import sys
import requests
from pymongo import MongoClient
import os
import random
import string


def generate_random_pass(n):
    return ''.join([random.choice(string.ascii_letters) for _ in range(n)])


def create_user(user):
    r = requests.put("http://api/users/register", json=user).json()
    print(r)


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

mongo = MongoClient("mongodb",
                    username=os.getenv("MONGODB_USER"),
                    password=os.getenv("MONGODB_PASS"))
db = mongo.secure_code_platform


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


if len(sys.argv) == 2:
    if sys.argv[1] == "create":
        create_test_users()
    elif sys.argv[1] == "remove":
        remove_test_users()
