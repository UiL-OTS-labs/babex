from datetime import date, datetime, timedelta

import pytest
from django.utils import timezone

from experiments.models import Appointment, Location, TimeSlot
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
def sample_experiment(admin_user, db, sample_location):
    yield admin_user.experiments.create(
        name="sample experiment",
        duration=10,
        session_duration=30,
        recruitment_target=50,
        task_description="task description",
        responsible_researcher="dr. Lin Guist",
        location=sample_location,
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


@pytest.fixture
def sample_location(db):
    yield Location.objects.create(name="Location")


@pytest.fixture
def appointment_tomorrow(db, sample_experiment, sample_leader, sample_participant):
    sample_experiment.leaders.add(sample_leader)
    start = datetime(
        date.today().year, date.today().month, date.today().day, 12, 0, tzinfo=timezone.get_current_timezone()
    ) + timedelta(days=1)
    timeslot = TimeSlot.objects.create(
        start=start,
        end=start + timedelta(hours=1),
        experiment=sample_experiment,
    )
    yield Appointment.objects.create(
        participant=sample_participant, experiment=sample_experiment, timeslot=timeslot, leader=sample_leader
    )
