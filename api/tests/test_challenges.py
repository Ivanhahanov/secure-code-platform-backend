from . import client


def test_challenges_list():
    response = client.post('/challenges/list')
    assert response.status_code == 200
