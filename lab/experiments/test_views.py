import json
from datetime import date, timedelta

from django.core.exceptions import BadRequest
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time
from rest_framework.test import APIRequestFactory, force_authenticate

from main.models import User
from participants.models import Participant

from .models import Experiment
from .views.call_views import AppointmentConfirm
from .views.invite_views import InviteParticipantsForExperimentView


class AppointmentTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="test", is_staff=True)
        cls.experiment = Experiment.objects.create()
        cls.experiment.leaders.add(cls.user)

        cls.participant = Participant.objects.create(
            dyslexic_parent=False,  # this is not nullable at the moment of writing the test
        )

    def setUp(self):
        self.factory = APIRequestFactory()

    def test_appointment_confirm(self):
        data = {
            "experiment": self.experiment.pk,
            "start": timezone.now() + timedelta(days=1),
            "end": timezone.now() + timedelta(days=1, hours=1),
            "leader": self.user.pk,
            "participant": self.participant.pk,
            "emailParticipant": False,
        }

        request = self.factory.post("/experiments/call/appointment/", data, format="json")
        force_authenticate(request, self.user)
        response = AppointmentConfirm.as_view()(request)
        self.assert_(json.loads(response.content))

    def test_appointment_confirm_fail_in_past(self):
        data = {
            "experiment": self.experiment.pk,
            "start": timezone.now() - timedelta(hours=2),
            "end": timezone.now() - timedelta(hours=1),
            "leader": self.user.pk,
            "participant": self.participant.pk,
            "emailParticipant": False,
        }

        request = self.factory.post("/experiments/call/appointment/", data, format="json")
        force_authenticate(request, self.user)
        with self.assertRaises(BadRequest):
            AppointmentConfirm.as_view()(request)


class InviteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="test", is_staff=True)
        cls.experiment = Experiment.objects.create()
        cls.experiment.leaders.add(cls.user)

        cls.participant = Participant.objects.create(
            dyslexic_parent=False,  # TODO: this is not nullable at the moment of writing the test
            email_subscription=True,  # TODO: this shouldn't have an effect on exclusions
            language="nl",  # default experiment language
        )

        cls.experiment.defaultcriteria.min_age_days = 0
        cls.experiment.defaultcriteria.min_age_months = 2
        cls.experiment.defaultcriteria.save()

    def setUp(self):
        self.factory = APIRequestFactory()

    @freeze_time("2021-03-01")
    def test_can_invite_participant_correct_min_age(self):
        self.participant.birth_date = date(2021, 1, 1)
        self.participant.save()

        request = self.factory.get(f"/experiments/{self.experiment.pk}/invite/")
        request.user = self.user
        response = InviteParticipantsForExperimentView.as_view()(request, experiment=self.experiment.pk)

        self.assertEqual(len(response.context_data["object_list"]), 1)

    @freeze_time("2021-03-01")
    def test_can_invite_participant_within_two_weeks(self):
        self.participant.birth_date = date(2021, 1, 14)
        self.participant.save()

        request = self.factory.get(f"/experiments/{self.experiment.pk}/invite/")
        request.user = self.user
        response = InviteParticipantsForExperimentView.as_view()(request, experiment=self.experiment.pk)

        self.assertEqual(len(response.context_data["object_list"]), 1)

    @freeze_time("2021-03-01")
    def test_cannot_invite_participant_when_too_young(self):
        self.participant.birth_date = date(2021, 1, 20)
        self.participant.save()

        request = self.factory.get(f"/experiments/{self.experiment.pk}/invite/")
        request.user = self.user
        response = InviteParticipantsForExperimentView.as_view()(request, experiment=self.experiment.pk)

        self.assertEqual(len(response.context_data["object_list"]), 0)
