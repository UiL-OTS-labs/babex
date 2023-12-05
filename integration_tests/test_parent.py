import datetime
import random
import string

import pytest
from selenium.webdriver.common.keys import Keys
from django.utils import timezone


@pytest.fixture
def default_signup_fill_form(sb, apps):
    """opens the signup form and fills some default values. individual tests should overwrite as necessary"""
    sb.open(apps.parent.url + 'signup/')

    sb.type('#id_name', 'Test Baby')
    sb.click('#id_sex_0')

    sb.select_option_by_text('#id_birth_date_month', 'March')
    sb.select_option_by_text('#id_birth_date_day', '5')
    sb.select_option_by_text('#id_birth_date_year', str(datetime.datetime.now().year - 1))

    sb.click('#id_birth_weight_1')
    sb.click('#id_pregnancy_duration_1')
    sb.click('#id_dyslexic_parent_3')
    sb.click('#id_tos_parent_0')
    sb.click('#id_languages_mono_dutch')

    sb.type('#id_parent_first_name', 'Test')
    sb.type('#id_parent_last_name', 'Parent')
    sb.type('#id_phonenumber', '06412345678')
    sb.type('#id_phonenumber_alt', '06487654321')

    sb.type('#id_email', 'parent@example.com')
    sb.type('#id_email_again', 'parent@example.com')

    sb.click('#id_save_longer_0')
    sb.click('#id_english_contact_0')
    sb.click('#id_newsletter_0')
    # use js_click instead of click, because if these are not visible (below view),
    # then a normal click will sometimes not work
    sb.js_click('#id_data_consent_0')


@pytest.fixture
def signup(sb, apps, default_signup_fill_form):
    suffix = ''.join(random.choice(string.digits) for i in range(4))
    email = f'parent{suffix}@localhost.local'

    sb.type('#id_email', email)
    sb.type('#id_email_again', email)
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


def test_signup_no_english(sb, apps, default_signup_fill_form):
    Signup = apps.lab.get_model('signups', 'Signup')

    sb.click('#id_english_contact_1')
    sb.click('input[type="submit"]')

    # check that the form was submitted
    sb.assert_element_not_visible('input[type="submit"]')
    assert 'signup/done' in sb.get_current_url()

    signup = Signup.objects.last()
    # verify the fields were saved correctly
    assert signup.english_contact is False


def test_signup_monolingual_dutch(sb, apps, default_signup_fill_form):
    Signup = apps.lab.get_model('signups', 'Signup')

    sb.click('#id_languages_mono_dutch')
    sb.click('input[type="submit"]')

    # check that the form was submitted
    sb.assert_element_not_visible('input[type="submit"]')
    assert 'signup/done' in sb.get_current_url()

    signup = Signup.objects.last()
    # verify the fields were saved correctly
    assert signup.languages == ['Nederlands']


def test_signup_multilingual_with_custom(sb, apps, default_signup_fill_form, as_admin):
    Signup = apps.lab.get_model('signups', 'Signup')
    Participant = apps.lab.get_model('participants', 'Participant')

    sb.click('#id_languages_multi')
    # select one language that's already on the list of known languages
    sb.select_option_by_text('#id_languages_multi_select', 'Engels')

    # type in one new language
    search_field = 'input.select2-search__field'
    sb.click(search_field)
    sb.send_keys(search_field, 'Afrikaans')
    sb.send_keys(search_field, Keys.RETURN)

    sb.click('input[type="submit"]')

    # check that the form was submitted
    sb.assert_element_not_visible('input[type="submit"]')
    assert 'signup/done' in sb.get_current_url()

    signup = Signup.objects.last()
    # verify the fields were saved correctly
    assert signup.languages == ['Engels', 'Afrikaans']

    # approve signup
    signup.email_verified = timezone.now()
    signup.save()
    sb.switch_to_driver(as_admin)
    sb.click("a:contains(Participants)")
    sb.click("a:contains(Signups)")
    sb.click("tr:contains(details) a")
    sb.click("button:contains(Approve)")

    # check that the languages were saved correctly
    participant = Participant.objects.last()
    assert participant.languages.values_list('name', flat=True)


def test_signup_save_longer(sb, apps, default_signup_fill_form):
    Signup = apps.lab.get_model('signups', 'Signup')

    sb.click('#id_save_longer_0')
    sb.click('input[type="submit"]')

    # check that the form was submitted
    sb.assert_element_not_visible('input[type="submit"]')
    assert 'signup/done' in sb.get_current_url()

    signup = Signup.objects.last()
    # verify the fields were saved correctly
    assert signup.save_longer is True


def test_signup_unborn(sb, apps, default_signup_fill_form):
    Signup = apps.lab.get_model('signups', 'Signup')

    now = datetime.datetime.now()
    sb.select_option_by_text('#id_birth_date_year', str(now.year))
    sb.select_option_by_text('#id_birth_date_month', now.strftime('%B'))
    sb.select_option_by_text('#id_birth_date_day', str(now.day + 1))

    sb.click('input[type="submit"]')

    # check that the form was submitted
    sb.assert_element_visible('select.is-invalid')
