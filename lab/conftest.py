from datetime import date

import pytest

from experiments.models import DefaultCriteria
from main.models import User
from participants.models import Participant


@pytest.fixture
def admin_user(db):
    admin = User.objects.create(
        username="admin", is_superuser=True, is_staff=True, name="Admin McAdmin", phonenumber="12345678"
    )
    admin.set_password("admin")
    admin.save()
    yield admin


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
        dyslexic_parent=False,
        language="nl",
        capable=True,
        email_subscription=True,
    )


@pytest.fixture
def sample_leader(db):
    yield User.objects.create(name="Leader McLeader", username="leader", phonenumber="23456789")
