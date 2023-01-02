import json
from datetime import datetime, timedelta
from django.test import TestCase
from django.utils import timezone

from rest_framework.test import APIRequestFactory, force_authenticate

from main.models import User
from leaders.models import Leader
from participants.models import Participant
from .models import Experiment
from .views.call_views import AppointmentConfirm


class AppointmentTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='test', is_staff=True)
        cls.leader = Leader.objects.create(user=cls.user)
        cls.experiment = Experiment.objects.create()
        cls.experiment.leaders.add(cls.leader)

        cls.participant = Participant.objects.create(
            dyslexic_parent=False,  # this is not nullable at the moment of writing the test
        )

    def setUp(self):
        self.factory = APIRequestFactory()

    def test_appointment_confirm(self):
        data = {
            'experiment': self.experiment.pk,
            'start': timezone.now() + timedelta(days=1),
            'end': timezone.now() + timedelta(days=1, hours=1),
            'leader': self.leader.pk,
            'participant': self.participant.pk,
            'emailParticipant': False
        }

        request = self.factory.post('/experiments/call/appointment/', data, format='json')
        force_authenticate(request, self.user)
        response = AppointmentConfirm.as_view()(request)
        self.assert_(json.loads(response.content))

    def test_appointment_confirm_fail_in_past(self):
        data = {
            'experiment': self.experiment.pk,
            'start': timezone.now() - timedelta(hours=2),
            'end': timezone.now() - timedelta(hours=1),
            'leader': self.leader.pk,
            'participant': self.participant.pk,
            'emailParticipant': False
        }

        request = self.factory.post('/experiments/call/appointment/', data, format='json')
        force_authenticate(request, self.user)
        with self.assertRaises(Exception):
            AppointmentConfirm.as_view()(request)
