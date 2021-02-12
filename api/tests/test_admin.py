from . import *


def test_containers_list():
    token = get_admin_token()
    headers = {"Authorization": "Bearer " + token}
    response = client.get("/admin/containers_list", headers=headers)
    assert response.status_code == 200
    assert 'securecodeplatform_api' in response.text
    assert 'securecodeplatform_mongo' in response.text
    assert 'securecodeplatform_redis' in response.text


def test_admin_users():
    token = get_token()
    admin_token = get_admin_token()
    headers = {"Authorization": "Bearer " + token}
    response = client.get("/admin/users", headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"] == 'Non admin user'

    headers = {"Authorization": "Bearer " + admin_token}
    response = client.get("/admin/users", headers=headers)
    data = response.json()
    assert response.status_code == 200
    assert type(data['users']) is list