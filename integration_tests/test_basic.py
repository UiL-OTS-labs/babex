import requests
from time import sleep


def test_services_start(apps):
    response = requests.get(apps.parent.url + 'status')
    assert response.ok
    status = response.json()
    for i in range(5):
        if status['ok']:
            return
        sleep(1)

    assert False
