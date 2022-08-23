from datetime import datetime, timedelta

from django.test import TestCase
from django.utils.timezone import get_current_timezone

from auditlog.models import LogEntry
from .common import _create_dummy_user, _create_thresholds, _create_experiment, \
    _create_participant
from experiments.models import Invitation, TimeSlot
from ..utils.invitations import delete_invites, get_invite_counts


class InvitationTests(TestCase):
    databases = ['default', 'auditlog']

    def setUp(self) -> None:
        _create_thresholds()
        self.experiment = _create_experiment()
        self.participants = [_create_participant(str(i)) for i in range(10)]

        for participant in self.participants:
            Invitation.objects.create(
                participant=participant,
                experiment=self.experiment,
            )

    def test_correct_num_without_timeslot(self):
        """Tests whether experiments without timeslots are ignored. """
        self.assertEqual(
            len(get_invite_counts()),
            0
        )

    def test_correct_num_with_current_timeslot(self):
        """Tests wheter experiments with a timeslot below the threshold are
        ignored"""
        timeslot = TimeSlot()
        timeslot.experiment = self.experiment
        timeslot.max_places = 1
        timeslot.datetime = datetime.now(tz=get_current_timezone())
        timeslot.save()

        self.assertEqual(len(get_invite_counts()), 0)

    def test_correct_num_with_old_timeslot(self):
        """Tests wheter experiments with a timeslot above the threshold are
        ignored"""
        timeslot = TimeSlot()
        timeslot.experiment = self.experiment
        timeslot.max_places = 1
        timeslot.datetime = datetime.now(tz=get_current_timezone()) - \
                            timedelta(days=20)
        timeslot.save()

        counts = get_invite_counts()

        # Check if the experiment is listed
        self.assertEqual(
            len(counts),
            1
        )

        # Check if the comment count is right
        self.assertEqual(
            counts[0][1],
            len(self.participants)
        )

    def test_delete(self):
        """Tests whether the delete_invites function actually deletes
        something"""
        # Just to make sure we're not testing something that is already 0
        self.assertNotEqual(Invitation.objects.count(), 0)

        delete_invites(self.experiment, _create_dummy_user())

        self.assertEqual(Invitation.objects.count(), 0)

        # Check if the auditlog logged anything
        # self.assertEqual(LogEntry.objects.count(), 1)
