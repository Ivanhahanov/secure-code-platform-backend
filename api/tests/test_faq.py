from . import *

test_id = ""


def test_add_question():
    global test_id
    token = get_admin_token()
    headers = {"Authorization": "Bearer " + token}
    data = {
        "question": "3",
        "answer": "3"
    }
    response = client.put('/faq/add', headers=headers, json=data)
    test_id = response.json()["_id"]
    print(type(test_id))
    assert response.status_code == 200


def test_update_question():
    token = get_admin_token()
    headers = {"Authorization": "Bearer " + token}
    data = {
        "_id": test_id,
        "question": "3",
        "answer": "3"
    }
    response = client.post('/faq/update', headers=headers, json=data)
    assert response.status_code == 200


def test_list_question():
    token = get_token()
    headers = {"Authorization": "Bearer " + token}
    response = client.get('/faq/list', headers=headers)
    assert response.status_code == 200
    test_id_flag = False
    for question in response.json():
        if question['_id'] == test_id:
            test_id_flag = True
    assert test_id_flag is True


def test_delete_question():
    token = get_admin_token()
    headers = {"Authorization": "Bearer " + token}
    data = {
        "_id": test_id
    }
    response = client.delete('/faq/del', headers=headers, params=data)
    assert response.status_code == 200
