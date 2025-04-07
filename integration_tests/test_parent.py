import datetime
import random
import string

import pytest
from django.utils import timezone

from playwright.sync_api import Page, expect


@pytest.fixture
def default_signup_fill_form(page: Page, apps):
    """opens the signup form and fills some default values. individual tests should overwrite as necessary"""
    page.goto(apps.parent.url + "signup/")

    page.fill("#id_name", "Test Baby")
    page.click("#id_sex_0")

    page.locator("#id_birth_date_month").select_option("March")
    page.locator("#id_birth_date_day").select_option("5")
    page.locator("#id_birth_date_year").select_option(
        str(datetime.datetime.now().year - 1)
    )

    page.click("#id_birth_weight_1")
    page.click("#id_pregnancy_duration_1")
    page.click("#id_dyslexic_parent_3")
    page.click("#id_tos_parent_0")
    page.click("#id_languages_mono_dutch")

    page.fill("#id_parent_first_name", "Test")
    page.fill("#id_parent_last_name", "Parent")
    page.fill("#id_phonenumber", "06412345678")
    page.fill("#id_phonenumber_alt", "06487654321")

    page.fill("#id_email", "parent@example.com")
    page.fill("#id_email_again", "parent@example.com")

    page.click("#id_save_longer_0")
    page.click("#id_english_contact_0")
    page.click("#id_newsletter_0")
    page.click("#id_data_consent_0")


@pytest.fixture
def signup(page: Page, apps, default_signup_fill_form):
    def delegate():
        suffix = "".join(random.choice(string.digits) for i in range(4))
        email = f"parent{suffix}@localhost.local"

        page.fill("#id_email", email)
        page.fill("#id_email_again", email)
        page.click('input[type="submit"]')

        # check that the form was submitted
        expect(page.locator('input[type="submit"]')).not_to_be_visible()
        assert "signup/done" in page.url

        return email

    return delegate


def test_parent_login(page, apps, signup, as_admin, link_from_mail, login_as):
    # confirm signup email
    address = signup()
    if link := link_from_mail(address, "Bevestiging"):
        page.goto(link)
    else:
        pytest.fail("could not find validation link")

    # approve signup
    as_admin.get_by_role("button", name="Participants").click()
    as_admin.locator("a").get_by_text("Signups").click()
    as_admin.locator("a").get_by_text("details").click()
    as_admin.locator("button").get_by_text("Approve").click()

    # try to login via email
    login_as(address)

    # check that login worked
    expect(page.get_by_text("Appointments")).to_be_visible()


def test_parent_login_unapproved(signup, apps, page, link_from_mail, login_as):
    # confirm signup email
    address = signup()
    if link := link_from_mail(address, "Bevestiging"):
        page.goto(link)
    else:
        pytest.fail("could not find validation link")

    # make sure that no login email has arrived
    assert login_as(address) is False


def test_parent_self_deactivate(page, participant, login_as, mailbox):
    email = participant.email
    login_as(email)

    page.get_by_text("Data management").click()
    page.on("dialog", lambda dialog: dialog.accept())
    page.get_by_text("Remove from").click()
    page.get_by_text("Remove from").wait_for(state="hidden")

    participant.refresh_from_db()
    assert participant.deactivated

    assert len(mailbox(email)) == 2
    assert (
        "bevestiging van uitschrijven" in mailbox(email)[0]["subject"]
        or "bevestiging van uitschrijven" in mailbox(email)[1]["subject"]
    )


def test_parent_login_deactivated(participant, apps, page, link_from_mail, login_as):
    email = participant.email
    participant.deactivate()
    assert login_as(email) is False


def test_signup_no_english(page, apps, default_signup_fill_form):
    Signup = apps.lab.get_model("signups", "Signup")

    page.click("#id_english_contact_1")
    page.click('input[type="submit"]')

    # check that the form was submitted
    expect(page.locator('input[type="submit"]')).not_to_be_visible()
    assert "signup/done" in page.url

    signup = Signup.objects.last()
    # verify the fields were saved correctly
    assert signup.english_contact is False


def test_signup_monolingual_dutch(page, apps, default_signup_fill_form):
    Signup = apps.lab.get_model("signups", "Signup")

    page.click("#id_languages_mono_dutch")
    page.click('input[type="submit"]')

    # check that the form was submitted
    expect(page.locator('input[type="submit"]')).not_to_be_visible()
    assert "signup/done" in page.url

    signup = Signup.objects.last()
    # verify the fields were saved correctly
    assert signup.languages == ["Nederlands"]


def test_signup_multilingual_with_custom(
    page, apps, default_signup_fill_form, as_admin
):
    Signup = apps.lab.get_model("signups", "Signup")
    Participant = apps.lab.get_model("participants", "Participant")

    page.click("#id_languages_multi")
    # select one language that's already on the list of known languages
    page.locator("#id_languages_multi_select").select_option("Engels")

    # type in one new language
    search_field = "input.select2-search__field"
    page.click(search_field)
    page.type(search_field, "Afrikaans")
    page.keyboard.press("Enter")

    page.click('input[type="submit"]')

    # check that the form was submitted
    expect(page.locator('input[type="submit"]')).not_to_be_visible()
    assert "signup/done" in page.url

    signup = Signup.objects.last()
    # verify the fields were saved correctly
    assert set(signup.languages) == set(["Engels", "Afrikaans"])

    # approve signup
    signup.email_verified = timezone.now()
    signup.save()
    as_admin.get_by_role("button", name="Participants").click()
    as_admin.locator("a").get_by_text("Signups").click()
    as_admin.locator("a").get_by_text("details").last.click()
    as_admin.locator("button").get_by_text("Approve").click()

    # check that the languages were saved correctly
    participant = Participant.objects.last()
    assert participant.languages.values_list("name", flat=True)


def test_signup_save_longer(page, apps, default_signup_fill_form):
    Signup = apps.lab.get_model("signups", "Signup")

    page.click("#id_save_longer_0")
    page.click('input[type="submit"]')

    # check that the form was submitted
    expect(page.locator('input[type="submit"]')).not_to_be_visible()
    assert "signup/done" in page.url

    signup = Signup.objects.last()
    # verify the fields were saved correctly
    assert signup.save_longer is True


def test_signup_unborn(page, apps, default_signup_fill_form):
    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
    page.locator("#id_birth_date_year").select_option(str(tomorrow.year))
    page.locator("#id_birth_date_month").select_option(tomorrow.strftime("%B"))
    page.locator("#id_birth_date_day").select_option(str(tomorrow.day))

    # should immediately show error
    expect(page.locator("select.is-invalid")).to_have_count(3)


def test_signup_confirmation_expired(page, apps, signup, as_admin, link_from_mail):
    # confirm signup email
    address = signup()

    Signup = apps.lab.get_model("signups", "Signup")
    s = Signup.objects.last()
    s.created = timezone.now() - datetime.timedelta(hours=49)
    s.save()

    if link := link_from_mail(address, "Bevestiging"):
        page.goto(link)
        expect(page.get_by_text("niet meer geldig")).to_be_visible()
    else:
        pytest.fail("could not find validation link")

    s = Signup.objects.last()
    assert s.email_verified is None


def test_parent_login_expired(participant, apps, page, link_from_mail, login_as):
    MailAuth = apps.lab.get_model("mailauth", "MailAuth")

    page.goto(apps.parent.url + "auth/")
    page.fill('input[name="email"]', participant.email)
    page.locator("button").get_by_text("Send").click()

    mauth = MailAuth.objects.last()
    mauth.expiry = timezone.now() - datetime.timedelta(seconds=1)
    mauth.save()

    link = link_from_mail(participant.email, "Link")
    page.goto(link)
    expect(page.get_by_text("verlopen")).to_be_visible()

    expect(page.get_by_text("Appointments")).not_to_be_visible()


def test_parent_login_multiple_children(participant, apps, page, login_as):
    first = participant
    Participant = apps.lab.get_model("participants", "Participant")
    second = Participant.objects.create(
        email=first.email,
        name="BabyTwo McBaby",
        parent_first_name=first.parent_first_name,
        parent_last_name=first.parent_last_name,
        birth_date=datetime.date(2023, 1, 1),
        phonenumber=first.phonenumber,
        dyslexic_parent=first.dyslexic_parent,
        email_subscription=True,
    )
    assert login_as(first.email) is True
    page.locator("a").get_by_text(first.name).click()
    page.wait_for_url("**/overview")
    expect(page.locator(".alert-error")).to_have_count(0)


def test_parent_login_with_existing_link_after_removal(participant, apps, page, link_from_mail, login_as):
    page.goto(apps.parent.url + "auth/")
    page.fill('input[name="email"]', participant.email)
    page.locator("button").get_by_text("Send").click()

    email = participant.email
    participant.deactivate()

    link = link_from_mail(email, "Link")
    page.goto(link)

    expect(page.get_by_text("login_failed")).to_be_visible()
    expect(page.get_by_text("Appointments")).not_to_be_visible()
