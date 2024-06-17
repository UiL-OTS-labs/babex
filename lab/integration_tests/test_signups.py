from datetime import datetime

import pytest
from django.utils import timezone
from playwright.sync_api import expect

from participants.models import Participant
from signups.models import Signup


@pytest.fixture
def sample_signup(db):
    yield Signup.objects.create(
        name="Test signup",
        sex="F",
        birth_date=datetime(2020, 4, 4),
        parent_first_name="Parent",
        parent_last_name="McParent",
        phonenumber="12345678",
        email="parent@localhost.local",
        english_contact=True,
        newsletter=True,
        dyslexic_parent=Participant.WhichParent.NEITHER,
        tos_parent=Participant.WhichParent.NEITHER,
        status=Signup.Status.NEW,
        email_verified=timezone.now(),
        birth_weight=Participant.BirthWeight._2500_TO_4500,
        pregnancy_duration=Participant.PregnancyDuration._37_TO_42,
        save_longer=False,
    )


def test_signup_approve(page, sample_signup, live_server, as_admin):
    page.get_by_role("button", name="Participants").click()
    page.locator("a").get_by_text("Signups").click()

    # check that the signup is visible somewhere within a table tag
    expect(page.locator("table").get_by_text(sample_signup.name)).to_be_visible()

    page.locator("a").get_by_text("details").click()
    page.locator("button").get_by_text("Approve").click()

    # check that the signup is no longer visible
    page.get_by_role("button", name="Participants").click()
    page.locator("a").get_by_text("Signups").click()
    expect(page.locator("table").get_by_text(sample_signup.name)).not_to_be_visible()

    # check that a new participant is visible in the system
    page.goto(live_server.url + "/participants/")
    expect(page.locator("table").get_by_text(sample_signup.name)).to_be_visible()


def test_signup_reject(page, sample_signup, live_server, as_admin):
    page.get_by_role("button", name="Participants").click()
    page.locator("a").get_by_text("Signups").click()

    page.locator("a").get_by_text("details").click()
    page.locator("button").get_by_text("Reject").click()

    # check that the signup is no longer visible
    page.get_by_role("button", name="Participants").click()
    page.locator("a").get_by_text("Signups").click()
    expect(page.locator("table").get_by_text(sample_signup.name)).not_to_be_visible()

    # check that no new participant is visible in the system
    page.goto(live_server.url + "/participants/")
    expect(page.locator("table").get_by_text(sample_signup.name)).not_to_be_visible()
