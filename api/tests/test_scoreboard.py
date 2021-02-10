from . import *

token = get_token()
headers = {"Authorization": "Bearer " + token}


def test_scoreboard_users():
    response = client.get('/scoreboard/users', headers=headers)
    data = response.json()
    assert response.status_code == 200
    assert data.get('username') is not None
    assert data.get('scoreboard') is not None


def test_scoreboard_info():
    response = client.get('/scoreboard/info', headers=headers)
    data = response.json()
    fields = ["username",
              "num_of_users",
              "num_of_challenges",
              "num_of_solved_challenges",
              "users_score",
              "users_place"]
    assert response.status_code == 200
    for field in fields:
        assert data.get(field) is not None

def test_get_num_of_users():
    response = client.get('/scoreboard/num_of_users')
    data = response.json()
    assert int(data['num_of_users']) > 0
