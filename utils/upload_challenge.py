import argparse
import os
import tarfile
import requests

parser = argparse.ArgumentParser()
parser.add_argument("dir", type=str,
                    help="display a square of a given number")
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


def upload_challenges():
    header = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTYxODc3MzkxMX0.BFfF7Ek-rzoZ1Kbz4HbTsZ2qZw-F6C_31KSA88ccxlE"}
    url = "http://localhost/challenges/upload_challenges"
    archive = {"archive": open("challenges.tar", 'rb')}
    r = requests.post(url, headers=header, files=archive)
    print(r.content)


if __name__ == '__main__':
    tar_directory()
    upload_challenges()
