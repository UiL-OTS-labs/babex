from datetime import datetime

import pytest
from django.utils import timezone

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


def test_signup_approve(sb, sample_signup, live_server, as_admin):
    sb.click("a:contains(Participants)")
    sb.click("a:contains(Signups)")

    # check that the signup is visible somewhere within a table tag
    sb.assert_text(sample_signup.name, "table")

    sb.click("tr:contains(details) a")
    sb.click("button:contains(Approve)")

    # check that the signup is no longer visible
    sb.click("a:contains(Participants)")
    sb.click("a:contains(Signups)")
    sb.assert_text_not_visible(sample_signup.name, "table")

    # check that a new participant is visible in the system
    sb.open(live_server.url + "/participants/")
    sb.assert_text(sample_signup.name, "table")


def test_signup_reject(sb, sample_signup, live_server, as_admin):
    sb.click("a:contains(Participants)")
    sb.click("a:contains(Signups)")

    sb.click("tr:contains(details) a")
    sb.click("button:contains(Reject)")

    # check that the signup is no longer visible
    sb.click("a:contains(Participants)")
    sb.click("a:contains(Signups)")
    sb.assert_text_not_visible(sample_signup.name, "table")

    # check that no new participant is visible in the system
    sb.open(live_server.url + "/participants/")
    sb.assert_text_not_visible(sample_signup.name, "table")
