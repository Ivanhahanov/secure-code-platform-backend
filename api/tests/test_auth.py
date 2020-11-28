from . import *


def test_users_token():
    data = {"username": "user", "password": "secret", }
    response = client.post('/users/token', data=data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()['token_type'] == 'bearer'


def test_users_me():
    token = get_token()
    headers = {"Authorization": "Bearer " + token}
    response = client.get('/users/me', headers=headers)
    assert response.status_code == 200


def test_bad_auth():
    data = {"username": "user", "password": "sec", }
    response = client.post('/users/token', data=data)
    assert response.status_code == 401
    assert response.json()['detail'] == 'Incorrect username or password'


def test_bad_token():
    headers = {"Authorization": "Bearer " + 'BadToken'}
    response = client.get('/users/me', headers=headers)
    assert response.status_code == 401
    assert response.json()['detail'] == 'Could not validate credentials'
