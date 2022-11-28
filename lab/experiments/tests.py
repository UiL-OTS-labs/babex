from datetime import datetime

from pytz import timezone
from dateutil.relativedelta import relativedelta
from django.test import TestCase

from main.models import User
from leaders.models import Leader
from participants.models import Participant, CriterionAnswer
from .models import Experiment, Criterion, ExperimentCriterion, Appointment, \
    Location, TimeSlot
from .utils.exclusion import get_eligible_participants_for_experiment


def _get_or_create_leader() -> Leader:
    if Leader.objects.exists():
        return Leader.objects.first()  # type: ignore
    user = User.objects.create()
    return Leader.objects.create(user=user)


def _get_or_create_location() -> Location:
    if Location.objects.exists():
        return Location.objects.first()  # type: ignore
    return Location.objects.create(name="Cyberspace")