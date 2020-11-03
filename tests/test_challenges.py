from . import client
import requests

def test_challenges_list():
    response = requests.post('http://localhost/challenges/list')
    assert response.status_code == 200
