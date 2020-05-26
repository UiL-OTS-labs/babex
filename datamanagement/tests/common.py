from datetime import datetime, timedelta

from django.test import TestCase
from django.utils.timezone import get_current_timezone

from datamanagement.models import Thresholds
from datamanagement.utils.common import get_thresholds_model
from experiments.models import Experiment, TimeSlot
from experiments.tests import _get_or_create_leader, _get_or_create_location
from main.models import User
from participants.models import Participant


def _create_thresholds() -> Thresholds:
    th = get_thresholds_model()
    th.participants_with_appointment = 10
    th.participants_without_appointment = 10
    th.participant_visibility = 10
    th.comments = 10
    th.invites = 10
    th.save()
    return th


def _create_experiment(timeslot_dts=None) -> Experiment:
    if timeslot_dts is None:
        timeslot_dts = []

    exp = Experiment.objects.create(
        name='test',
        leader=_get_or_create_leader(),
        location=_get_or_create_location(),
    )

    for timeslot_datetime in timeslot_dts:
        tm = TimeSlot()
        tm.experiment = exp
        tm.max_places = 100
        tm.datetime = timeslot_datetime
        tm.save()

    return exp


def _create_participant(name="dummy", creation_dt=None) -> Participant:
    participant = Participant.objects.create(
        name=name,
        dyslexic=False
    )

    if creation_dt:
        participant.created = creation_dt
        participant.save()

    return participant


def _create_dummy_user() -> User:
    if User.objects.exists():
        return User.objects.first()

    return User.objects.create(
        username="dummy"
    )


class CommonUtilsTests(TestCase):

    def test_create_thresholds(self):
        _create_thresholds()

        self.assertEqual(Thresholds.objects.count(), 1)

        thresholds = get_thresholds_model()
        self.assertIsNotNone(thresholds)

        self.assertEqual(thresholds.participants_with_appointment, 10)
        self.assertEqual(thresholds.participants_without_appointment, 10)
        self.assertEqual(thresholds.participant_visibility, 10)
        self.assertEqual(thresholds.comments, 10)
        self.assertEqual(thresholds.invites, 10)

    def test_create_experiment(self):
        experiment = _create_experiment()
        self.assertIsNotNone(experiment)
        self.assertIsInstance(experiment, Experiment)

        # Test if the auto-timeslot creation works
        now = datetime.now(tz=get_current_timezone())
        experiment = _create_experiment(
            [now, now]
        )
        self.assertIsNotNone(experiment)
        self.assertIsInstance(experiment, Experiment)
        self.assertEqual(experiment.timeslot_set.count(), 2)
        first_timeslot = experiment.timeslot_set.first()
        self.assertEqual(first_timeslot.datetime, now)

    def test_create_participant(self):
        participant = _create_participant()

        self.assertIsNotNone(participant)
        self.assertIsInstance(participant, Participant)
        self.assertEqual(participant.name, "dummy")
        self.assertIsNotNone(participant.created)

        # Test if created override works
        dt = datetime.now(tz=get_current_timezone()) - timedelta(days=1)
        participant = _create_participant(creation_dt=dt)

        self.assertIsNotNone(participant)
        self.assertIsInstance(participant, Participant)
        self.assertIsNotNone(participant.created)
        self.assertEqual(participant.created, dt)

    def test_create_dummy_user(self):
        user = _create_dummy_user()

        self.assertIsNotNone(user)
        self.assertIsInstance(user, User)
        self.assertEqual(User.objects.count(), 1)

        user2 = _create_dummy_user()
        self.assertEqual(user, user2)
        self.assertEqual(User.objects.count(), 1)

