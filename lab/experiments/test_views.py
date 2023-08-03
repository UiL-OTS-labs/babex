import json
from datetime import date, timedelta, datetime

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

from experiments.models import TimeSlot


class AppointmentTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="test", is_staff=True)
        cls.experiment = Experiment.objects.create()
        cls.experiment.leaders.add(cls.user)

        cls.participant = Participant.objects.create(dyslexic_parent="UNK")

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

    def test_appointment_confirm_when_eligible_age(self):
        self.experiment.defaultcriteria.min_age_days = 0
        self.experiment.defaultcriteria.min_age_months = 8
        self.experiment.defaultcriteria.save()

        # participant should be too young to participate
        self.participant.birth_date = timezone.now() - timedelta(days=8 * 30)
        self.participant.save()

        data = {
            "experiment": self.experiment.pk,
            "start": timezone.now() + timedelta(days=7),
            "end": timezone.now() + timedelta(days=7, hours=1),
            "leader": self.user.pk,
            "participant": self.participant.pk,
            "emailParticipant": False,
        }

        request = self.factory.post("/experiments/call/appointment/", data, format="json")
        force_authenticate(request, self.user)
        AppointmentConfirm.as_view()(request)

    def test_appointment_confirm_fail_when_ineligible(self):
        self.experiment.defaultcriteria.min_age_days = 0
        self.experiment.defaultcriteria.min_age_months = 8
        self.experiment.defaultcriteria.save()

        # participant should be too young to participate
        self.participant.birth_date = timezone.now() - timedelta(days=60)
        self.participant.save()

        data = {
            "experiment": self.experiment.pk,
            "start": timezone.now() + timedelta(days=7),
            "end": timezone.now() + timedelta(days=7, hours=1),
            "leader": self.user.pk,
            "participant": self.participant.pk,
            "emailParticipant": False,
        }

        request = self.factory.post("/experiments/call/appointment/", data, format="json")
        force_authenticate(request, self.user)
        with self.assertRaises(Exception):
            AppointmentConfirm.as_view()(request)


class InviteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="test", is_staff=True)
        cls.experiment = Experiment.objects.create()
        cls.experiment.leaders.add(cls.user)

        cls.participant = Participant.objects.create(
            dyslexic_parent="NO",
            multilingual=False,
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


# new test written in pytest style


def test_experiment_detail_view(admin_client, admin_user, sample_experiment, sample_participant):
    # make an appointment
    timeslot = TimeSlot.objects.create(
        start=datetime.now() + timedelta(hours=24),
        end=datetime.now() + timedelta(hours=25),
        experiment=sample_experiment,
    )
    appointment = sample_participant.appointments.create(
        experiment=sample_experiment, leader=admin_user, timeslot=timeslot
    )

    response = admin_client.get(f"/experiments/{sample_experiment.pk}/")

    assert appointment in response.context["appointments"].all()
