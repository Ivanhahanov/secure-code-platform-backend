from . import *
import requests


def test_challenges_list():
    token = get_token()
    headers = {"Authorization": "Bearer " + token}
    response = client.post('/challenges/list', headers=headers)
    assert response.status_code == 200
