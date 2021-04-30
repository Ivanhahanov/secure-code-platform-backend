import sys
import requests

if len(sys.argv) < 1:
    print("Please specify admin's pass")

user = {"username": "admin",
        "email": "admin@email.com",
        "full_name": "Admin",
        "disabled": False,
        "user_role": "user",
        "avatar_path": "",
        "password": sys.argv[1]}
r = requests.put("http://localhost/users/register", json=user).json()
print(r)

