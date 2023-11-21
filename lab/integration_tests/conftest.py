from datetime import date

import pytest

from experiments.models import DefaultCriteria
from main.models import User
from participants.models import Language, Participant


@pytest.fixture
def as_admin(sb, admin_user, live_server):
    admin_user.name = "Admin McAdmin"
    admin_user.phonenumber = "12345678"
    admin_user.save()

    sb.open(live_server.url + "/login")
    # sb.click('#djHideToolBarButton')
    sb.type("#id_username", "admin")
    sb.type("#id_password", "password")
    sb.click('button:contains("Log in")')


@pytest.fixture
def as_leader(sb, django_user_model, live_server):
    username = "test_user"
    password = "test_user"
    user = django_user_model.objects.create_user(username=username, password=password)
    sb.open(live_server.url + "/login")
    # sb.click('#djHideToolBarButton')
    sb.type("#id_username", username)
    sb.type("#id_password", password)
    sb.click('button:contains("Log in")')
    yield user


@pytest.fixture
def sample_experiment(admin_user, db):
    yield admin_user.experiments.create(
        defaultcriteria=DefaultCriteria.objects.create(dyslexia=DefaultCriteria.Dyslexia.INDIFFERENT)
    )


@pytest.fixture
def sample_participant(db):
    dutch = Language.objects.create(name="Nederlands")
    participant = Participant.objects.create(
        email="baby@baby.com",
        name="Baby McBaby",
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
