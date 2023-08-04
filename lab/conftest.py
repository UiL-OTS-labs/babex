from datetime import date

import pytest

from experiments.models import DefaultCriteria
from main.models import User
from participants.models import Participant


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
        dyslexic_parent=Participant.DyslexicParent.NEITHER,
        language="nl",
        email_subscription=True,
    )


@pytest.fixture
def sample_leader(db):
    yield User.objects.create(name="Leader McLeader", username="leader", phonenumber="23456789")
