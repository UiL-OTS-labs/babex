from datetime import date

import pytest

from experiments.models import DefaultCriteria
from main.models import User
from participants.models import Language, Participant


def set_language_english(page):
    loc = page.locator("button").get_by_text("English")
    if loc.count():
        loc.click()


@pytest.fixture
def as_admin(page, admin_user, live_server):
    admin_user.name = "Admin McAdmin"
    admin_user.phonenumber = "12345678"
    admin_user.save()

    page.goto(live_server.url + "/login")
    set_language_english(page)

    page.fill("#id_username", "admin")
    page.fill("#id_password", "password")
    page.locator("button").get_by_text("Log in").click()


@pytest.fixture
def as_leader(page, django_user_model, live_server):
    username = "test_user"
    password = "test_user"
    user = django_user_model.objects.create_user(username=username, password=password, name="Test Leader")
    page.goto(live_server.url + "/login")
    set_language_english(page)

    page.fill("#id_username", username)
    page.fill("#id_password", password)
    page.locator("button").get_by_text("Log in").click()
    yield user


@pytest.fixture
def sample_experiment(admin_user, db):
    yield admin_user.experiments.create(
        defaultcriteria=DefaultCriteria.objects.create(),
        name="sample experiment",
        duration="10 minutes",
        session_duration="30 minutes",
        recruitment_target=50,
        task_description="task description",
        additional_instructions="additional instructions",
        responsible_researcher="dr. Lin Guist",
    )


@pytest.fixture
def sample_participant(db):
    dutch = Language.objects.create(name="Nederlands")
    participant = Participant.objects.create(
        email="baby@baby.com",
        name="Baby McBaby",
        sex=Participant.Sex.UNKNOWN,
        parent_first_name="Parent",
        parent_last_name="McParent",
        birth_date=date(2020, 1, 1),
        phonenumber="987654321",
        dyslexic_parent=Participant.WhichParent.NEITHER,
        email_subscription=True,
    )
    participant.languages.add(dutch)
    yield participant


@pytest.fixture
def sample_leader(db):
    yield User.objects.create(name="Leader McLeader", username="leader", phonenumber="23456789")
