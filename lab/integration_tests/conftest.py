from datetime import date

import pytest

from experiments.models import DefaultCriteria
from main.models import User
from participants.models import Participant


@pytest.fixture
def as_admin(sb, admin_user, live_server):
    admin_user.name = "Admin McAdmin"
    admin_user.phonenumber = "12345678"
    admin_user.save()

    sb.open(live_server.url)
    # sb.click('#djHideToolBarButton')
    sb.type("#id_username", "admin")
    sb.type("#id_password", "password")
    sb.click('button:contains("Log in")')


@pytest.fixture
def as_leader(sb, django_user_model, live_server):
    username = "test_user"
    password = "test_user"
    user = django_user_model.objects.create_user(username=username, password=password)
    sb.open(live_server.url)
    # sb.click('#djHideToolBarButton')
    sb.type("#id_username", username)
    sb.type("#id_password", password)
    sb.click('button:contains("Log in")')
    yield user


@pytest.fixture
def sample_experiment(admin_user, db):
    yield admin_user.experiments.create(defaultcriteria=DefaultCriteria.objects.create())


@pytest.fixture
def sample_participant(db):
    yield Participant.objects.create(
        email="baby@baby.com",
        name="Baby McBaby",
        parent_name="Parent McParent",
        birth_date=date(2020, 1, 1),
        multilingual=False,
        phonenumber="987654321",
        dyslexic_parent="UNK",
        language="nl",
        capable=True,
        email_subscription=True,
    )


@pytest.fixture
def sample_leader(db):
    yield User.objects.create(name="Leader McLeader", username="leader", phonenumber="23456789")
