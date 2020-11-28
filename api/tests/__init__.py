from fastapi.testclient import TestClient
from api.app.server import app

client = TestClient(app)


def get_token():
    data = {"username": "user", "password": "secret", }
    response = client.post('/users/token', data=data)
    return response.json()['access_token']


def get_admin_token():
    data = {"username": "admin", "password": "secret", }
    response = client.post('/users/token', data=data)
    return response.json()['access_token']
