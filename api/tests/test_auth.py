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