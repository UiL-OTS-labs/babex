from django.test import TestCase

from main.models import User
from api.auth.models import ApiUser
from leaders.models import Leader
from participants.models import Participant


class AccountDeleteTests(TestCase):

    def test_participant_deletion(self):
        participant = Participant.objects.create(
            name='test',
            email='text@test.test2',
            phonenumber='654321',
            # required for the model
            dyslexic_parent=False,
            language='nl'
        )

        participant.api_user = ApiUser.objects.create()

        self.assertEqual(1, Participant.objects.count())
        self.assertEqual(1, ApiUser.objects.count())

        participant.delete()

        self.assertEqual(0, Participant.objects.count())
        self.assertEqual(0, User.objects.count())

    def test_leader_deletion(self):
        user = User.objects.create()

        leader = Leader.objects.create(user=user)

        self.assertEqual(1, Leader.objects.count())
        self.assertEqual(1, User.objects.count())

        leader.delete()

        self.assertEqual(0, Leader.objects.count())
        self.assertEqual(0, User.objects.count())
