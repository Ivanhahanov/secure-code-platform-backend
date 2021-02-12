from . import *
import requests

token = get_token()
headers = {"Authorization": "Bearer " + token}


def test_challenges_list():
    response = client.post('/challenges/list', headers=headers)
    assert response.status_code == 200


def test_challenges_category_list():
    category_list = [
        "web",
        "crypto",
        "forensic",
        "network",
        "linux",
        "reverse"
    ]
    response = client.get('/challenges/category_list', headers=headers)
    assert response.status_code == 200
    assert response.json()['category_list'] == category_list

