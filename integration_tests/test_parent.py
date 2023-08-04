import random
import string

import pytest


@pytest.fixture
def signup(sb, apps):
    suffix = ''.join(random.choice(string.digits) for i in range(4))
    email = f'parent{suffix}@localhost.local'
    sb.open(apps.parent.url + 'signup/')
    sb.type('#id_name', 'Test Baby')
    sb.click('#id_sex_0')

    sb.type('#id_birth_weight', '2200')
    sb.type('#id_pregnancy_weeks', '3')
    sb.type('#id_pregnancy_days', '1')

    sb.click('#id_dyslexic_parent_3')

    sb.type('#id_parent_name', 'Test Parent')
    sb.type('#id_phonenumber', '06412345678')
    sb.type('#id_email', email)

    # use js_click instead of click, because if these are not visible (below view),
    # then a normal click will sometimes not work
    sb.js_click('#id_data_consent')
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


def test_parent_self_deactivate(sb, participant, login_as):
    login_as(participant.email)

    sb.click('a:contains("Data management")')
    # using sb.click directly interferes with the confirm() dialog
    # so it's better to use find_element().click()
    sb.find_element('button:contains("Remove from")').click()
    sb.accept_alert()
    sb.wait_for_element_not_visible('button:contains("Remove from")')

    participant.refresh_from_db()
    assert participant.deactivated


def test_parent_login_deactivated(participant, apps, sb, link_from_mail, login_as):
    participant.deactivate()
    assert login_as(participant.email) is False
