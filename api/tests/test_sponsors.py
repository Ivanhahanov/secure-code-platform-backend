from . import *

test_id = ""


def test_add_sponsor():
    global test_id
    token = get_token()
    headers = {"Authorization": "Bearer " + token}
    data = {
        "title": "string",
        "description": "string",
        "img": "string"
    }
    response = client.put('/sponsors/add', headers=headers, json=data)
    test_id = response.json()['_id']
    print(type(test_id))
    assert response.status_code == 200


def test_update_sponsor():
    token = get_token()
    headers = {"Authorization": "Bearer " + token}
    data = {
        "_id": test_id,
        "title": "string",
        "description": "string",
        "img": "img"
    }
    response = client.post('/sponsors/update', headers=headers, json=data)
    assert response.status_code == 200


def test_list_sponsor():
    token = get_token()
    headers = {"Authorization": "Bearer " + token}
    response = client.get('/sponsors/list', headers=headers)
    assert response.status_code == 200


def test_delete_sponsor():
    token = get_token()
    headers = {"Authorization": "Bearer " + token}
    data = {
        "_id": test_id
    }
    response = client.delete('/sponsors/del', headers=headers, params=data)
    assert response.status_code == 200
