from . import *

headers = {"Authorization": "Bearer " + get_admin_token()}


def test_add_category():
    data = {
        "category_name": "test"
    }
    response = client.put("admin/category/add", headers=headers, json=data)
    answer = response.json()
    assert response.status_code == 200
    assert answer['status'] is True
    assert answer['category']['category_name'] == 'test'


def test_list_category():
    response = client.get("admin/category/list", headers=headers)
    answer = response.json()
    assert response.status_code == 200
    assert 'test' in list(map(lambda c: c['category_name'], answer['categories']))


def test_delete_category():
    data = {
        "category_name": "test"
    }
    response = client.delete("admin/category/delete", headers=headers, params=data)
    answer = response.json()
    assert response.status_code == 200
    assert answer['status'] is True


def test_add_tag():
    data = {
        "tag_name": "test",
        "tag_class": "test"
    }
    response = client.put("admin/tags/add", headers=headers, json=data)
    answer = response.json()
    assert response.status_code == 200
    assert answer['status'] is True
    assert answer['tag']['tag_name'] == 'test'
    assert answer['tag']['tag_class'] == 'test'


def test_list_tags():
    response = client.get("admin/tags/list", headers=headers)
    answer = response.json()
    assert response.status_code == 200
    assert 'test' in list(map(lambda c: c['tag_name'], answer['tags']))


def test_delete_tag():
    data = {
        "tag_name": "test"
    }
    response = client.delete("admin/tags/delete", headers=headers, params=data)
    answer = response.json()
    assert response.status_code == 200
    assert answer['status'] is True
