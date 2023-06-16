import random
import re
import string

import pytest
import requests


def test_services_start(apps):
    response = requests.get(apps.parent.url + 'status')
    assert response.ok
    status = response.json()
    assert status['ok']


@pytest.fixture
def signup(sb, apps):
    suffix = ''.join(random.choice(string.digits) for i in range(4))
    email = f'parent{suffix}@localhost.local'
    sb.open(apps.parent.url + 'signup/')
    sb.type('#id_name', 'Test Baby')
    sb.type('#id_parent_name', 'Test Parent')
    sb.type('#id_city', 'Townsville')
    sb.type('#id_phonenumber', '06412345678')
    sb.type('#id_email', email)
    sb.click('#id_sex_0')
    sb.click('#id_data_consent')
    sb.click('input[type="submit"]')

    # check that the form was submitted
    sb.assert_element_not_visible('input[type="submit"]')
    assert 'signup/done' in sb.get_current_url()

    return email


def test_parent_login(sb, apps, signup, as_admin, link_from_mail, login_as):
    # confirm signup email
    if link := link_from_mail(signup, 'validate'):
        sb.open(link)
    else:
        pytest.fail('could not find validation link')

    sb.switch_to_driver(as_admin)
    # approve signup
    sb.click("a:contains(Participants)")
    sb.click("a:contains(Signups)")
    sb.click("tr:contains(details) a")
    sb.click("button:contains(Approve)")

    # try to login via email
    login_as(signup)

    # check that login worked
    sb.assert_text_visible('Appointments')


def test_parent_login_unapproved(signup, apps, sb, link_from_mail, login_as):
    # confirm signup email
    if link := link_from_mail(signup, 'validate'):
        sb.open(link)
    else:
        pytest.fail('could not find validation link')

    # make sure that no login email has arrived
    assert login_as(signup) is False
