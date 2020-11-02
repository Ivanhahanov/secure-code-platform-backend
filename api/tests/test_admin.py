from . import client

def test_containers_list():
    response = client.get("/admin/containers_list")
    assert response.status_code == 200
    assert 'securecodeplatform_api' in response.text
    assert 'mongo' in response.text