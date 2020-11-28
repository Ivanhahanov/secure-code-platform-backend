from . import *

def test_containers_list():
    token = get_admin_token()
    headers = {"Authorization": "Bearer " + token}
    response = client.get("/admin/containers_list", headers=headers)
    assert response.status_code == 200
    assert 'securecodeplatform_api' in response.text
    assert 'securecodeplatform_mongo' in response.text
    assert 'securecodeplatform_redis' in response.text
