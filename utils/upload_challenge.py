import argparse
import os
import tarfile
import requests

parser = argparse.ArgumentParser()
parser.add_argument("dir", type=str,
                    help="directory for compress")
parser.add_argument("-u", "--username", type=str,
                    help="user with editor or admin credentials")
parser.add_argument("-p", "--password", type=str,
                    help="users password")
parser.add_argument("-U", "--url", type=str,
                    help="url of platform", default="localhost")
args = parser.parse_args()


def tar_directory():
    if os.path.isdir(args.dir):
        description = os.path.join(args.dir, "description.yml")
        if os.path.isfile(description):
            with tarfile.open("challenges.tar", "w") as tar:
                for name in os.listdir(args.dir):
                    tar.add(os.path.join(args.dir, name))
                print("Successfully compressed")
                return
    print("Directory doesn't exists")
    exit(1)


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


def upload_challenges():
    token = get_token()
    header = {
        "Authorization": f"Bearer {token}"}
    url = f"http://{args.url}/challenges/upload_challenges"
    archive = {"archive": open("challenges.tar", 'rb')}
    r = requests.post(url, headers=header, files=archive)
    print(*r.json().values())


if __name__ == '__main__':
    tar_directory()
    upload_challenges()
