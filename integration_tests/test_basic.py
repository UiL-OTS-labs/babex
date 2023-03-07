import re
import pytest
import requests


def test_services_start(apps):
    response = requests.get(apps.parent.url + 'status')
    assert response.ok
    status = response.json()
    assert status['ok']


@pytest.fixture
def signup(sb, apps):
    email = 'parent@localhost.local'
    sb.open(apps.parent.url + 'signup/')
    sb.type('#id_name', 'Test Baby')
    sb.type('#id_parent_name', 'Test Parent')
    sb.type('#id_city', 'Townsville')
    sb.type('#id_phonenumber', '06412345678')
    sb.type('#id_email', email)
    sb.click('#id_sex_0')
    sb.click('#id_data_consent')
    sb.click('input[type="submit"]')

    sb.assert_text_visible('signup_done')
    return email


def test_parent_login(sb, apps, signup, as_admin, mailbox):
    sb.switch_to_driver(as_admin)
    # approve signup
    sb.click("a:contains(Participants)")
    sb.click("a:contains(Signups)")
    sb.click("tr:contains(details) a")
    sb.click("button:contains(Approve)")

    # try to login via email
    sb.switch_to_default_driver()
    sb.open(apps.parent.url)
    sb.type('input[name="email"]', signup)
    sb.click('button:contains("Send")')

    mail = mailbox(signup)
    assert len(mail)
    html = mail[0].get_payload()[1].get_payload()
    # find link in email
    link = re.search(r'<a href="([^"]+)"', html).group(1)
    sb.open(link)

    # check that login worked
    sb.assert_text_visible('Welcome')
