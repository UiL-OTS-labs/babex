import requests


def test_services_start(apps):
    response = requests.get(apps.parent.url + 'status')
    assert response.ok
    status = response.json()
    assert status['ok']
