from django.test import TestCase
from django.contrib.auth import get_user_model
from api.auth.models import ApiUser
from comments.models import Comment
from leaders.models import Leader
from participants.models import Participant, SecondaryEmail
from ..utils.create_participant_account import ReturnValues, \
    create_participant_account


class ParticipantAccountCreationTests(TestCase):

    fixtures = ('api_groups',)

    def setUp(self) -> None:
        get_user_model().objects.create(
            username="admin",
            is_supreme_admin=True,
        )

    def test_simple_creation(self):
        self.assertEqual(
            Participant.objects.count(),
            0
        )
        self.assertEqual(
            ApiUser.objects.count(),
            0
        )

        ret = create_participant_account(
            email="test@test.nl",
            name='Test',
            multilingual=True,
            language='nl',
            dyslexic_parent=True,
            mailing_list=True
        )

        self.assertEqual(
            ret,
            ReturnValues.OK
        )

        self.assertEqual(
            Participant.objects.count(),
            1
        )
        self.assertEqual(
            ApiUser.objects.count(),
            1
        )

        user = ApiUser.objects.first()
        participant = Participant.objects.first()

        self.assertTrue(user.is_participant)
        self.assertEqual(user.participant, participant)
        self.assertEqual(participant.api_user, user)

    def test_existing_participant(self):
        """
        This testcase tests creating an account for a participant that
        already is in the database
        :return:
        """

        participant = Participant.objects.create(
            email='test@test.nl',
            dyslexic_parent=False
        )

        self.assertEqual(
            Participant.objects.count(),
            1
        )
        self.assertEqual(
            ApiUser.objects.count(),
            0
        )

        ret = create_participant_account(
            email="test@test.nl",
            name='Test',
            multilingual=True,
            language='nl',
            dyslexic_parent=True,
            mailing_list=True
        )

        self.assertEqual(
            ret,
            ReturnValues.OK
        )

        self.assertEqual(
            Participant.objects.count(),
            1
        )
        self.assertEqual(
            ApiUser.objects.count(),
            1
        )

        # Check if dyslexic_parent is still the same
        # This should not be modifiable by any action on the users part
        p = Participant.objects.get(pk=1)
        self.assertEqual(p.dyslexic_parent, False)

        user = ApiUser.objects.first()

        self.assertTrue(user.is_participant)
        self.assertEqual(user.participant, participant)
        self.assertEqual(p.api_user, user)

    def test_multiple_existing_participants(self):
        """
        This testcase tests creating an account with an email that's linked
        to 2 existing participants (without an account linked).

        Intended behaviour is that a new participant is added with an
        account, and a comment is added
        :return:
        """
        Participant.objects.create(
            email='test@test.nl',
            dyslexic_parent=False
        )

        p = Participant.objects.create(
            email='test@test.be',
            dyslexic_parent=False
        )

        SecondaryEmail.objects.create(
            email='test@test.nl',
            participant=p
        )

        SecondaryEmail.objects.create(
            email='test@test.nl',
            participant=p
        )

        self.assertEqual(
            Participant.objects.count(),
            2
        )
        self.assertEqual(
            ApiUser.objects.count(),
            0
        )

        ret = create_participant_account(
            email="test@test.nl",
            name='Test',
            multilingual=True,
            language='nl',
            dyslexic_parent=True,
            mailing_list=True
        )

        self.assertEqual(
            ret,
            ReturnValues.OK
        )

        self.assertEqual(
            Participant.objects.count(),
            3
        )
        self.assertEqual(
            ApiUser.objects.count(),
            1
        )
        self.assertEqual(
            Comment.objects.count(),
            1
        )

    def test_existing_participant_with_account(self):
        u = ApiUser.objects.create(
            email='test@test.nl',
        )

        p1 = Participant.objects.create(
            email='test@test.nl',
            dyslexic_parent=False,
            api_user=u
        )

        self.assertEqual(
            Participant.objects.count(),
            1
        )
        self.assertEqual(
            ApiUser.objects.count(),
            1
        )

        ret = create_participant_account(
            email="test@test.nl",
            name='Test',
            multilingual=True,
            language='nl',
            dyslexic_parent=True,
            mailing_list=True
        )

        self.assertEqual(
            ret,
            ReturnValues.ACCOUNT_ALREADY_EXISTS
        )
        self.assertEqual(
            ApiUser.objects.count(),
            1
        )
        self.assertEqual(
            Participant.objects.count(),
            1
        )
        self.assertTrue(u.is_participant)

    def test_multiple_existing_participants_with_account(self):
        """
        This testcase tests the behaviour when there are multiple
        participants associated to the same email, all with accounts of their
        own.
        :return:
        """

        u1 = ApiUser.objects.create(
            email='test@test.nl',
        )

        u2 = ApiUser.objects.create(
            email='test@test.be',
        )

        p1 = Participant.objects.create(
            email='test@test.nl',
            dyslexic_parent=False,
            api_user=u1,
        )

        p2 = Participant.objects.create(
            email='test@test.be',
            dyslexic_parent=False,
            api_user=u2,
        )

        SecondaryEmail.objects.create(
            email='test@test.nl',
            participant=p2
        )

        self.assertEqual(
            Participant.objects.count(),
            2
        )
        self.assertEqual(
            ApiUser.objects.count(),
            2
        )

        ret = create_participant_account(
            email="test@test.nl",
            name='Test',
            multilingual=True,
            language='nl',
            dyslexic_parent=True,
            mailing_list=True
        )

        self.assertEqual(
            ret,
            ReturnValues.ACCOUNT_ALREADY_EXISTS
        )

        self.assertEqual(
            Participant.objects.count(),
            2
        )
        self.assertEqual(
            ApiUser.objects.count(),
            2
        )

        self.assertTrue(u1.is_participant)
        self.assertTrue(u2.is_participant)
        self.assertEqual(u1.participant, p1)
        self.assertEqual(u2.participant, p2)

    def test_existing_leader_account(self):
        """
        This testcase tests adding a participant profile to an existing
        leader account.
        :return:
        """
        u = ApiUser.objects.create(
            email='test@test.nl',
        )

        Leader.objects.create(
            name='Test',
            phonenumber='00-0000000',
            api_user=u
        )

        self.assertEqual(
            Participant.objects.count(),
            0
        )
        self.assertEqual(
            ApiUser.objects.count(),
            1
        )
        self.assertEqual(
            Leader.objects.count(),
            1
        )

        self.assertEqual(
            u.is_participant,
            False
        )
        self.assertEqual(
            u.is_leader,
            True
        )

        ret = create_participant_account(
            email="test@test.nl",
            name='Test',
            multilingual=True,
            language='nl',
            dyslexic_parent=True,
            mailing_list=True
        )

        self.assertEqual(
            ret,
            ReturnValues.OK
        )

        self.assertEqual(
            Participant.objects.count(),
            1
        )
        self.assertEqual(
            ApiUser.objects.count(),
            1
        )
        self.assertEqual(
            Leader.objects.count(),
            1
        )

        # Refetch to make sure we have the latest data
        u = ApiUser.objects.get(email='test@test.nl')

        self.assertEqual(
            u.is_participant,
            True
        )
        self.assertEqual(
            u.is_leader,
            True
        )

    def test_email_switch(self):
        """
        This testcase tests if the main and secondary emails are switched
        properly.
        :return:
        """
        p = Participant.objects.create(
            email='test@test.be',
            dyslexic_parent=False
        )

        SecondaryEmail.objects.create(
            email='test@test.nl',
            participant=p
        )

        self.assertEqual(
            Participant.objects.count(),
            1
        )
        self.assertEqual(
            ApiUser.objects.count(),
            0
        )

        ret = create_participant_account(
            email="test@test.nl",
            name='Test',
            multilingual=True,
            language='nl',
            dyslexic_parent=True,
            mailing_list=True
        )

        self.assertEqual(
            ret,
            ReturnValues.OK
        )

        self.assertEqual(
            Participant.objects.count(),
            1
        )
        self.assertEqual(
            ApiUser.objects.count(),
            1
        )

        # Refetch to get the latest data
        p = Participant.objects.get(pk=1)

        # Check if the primary email is now the .nl variant
        self.assertEqual(
            p.email,
            'test@test.nl'
        )

        self.assertEqual(
            p.secondaryemail_set.count(),
            1
        )

        secondary_email = p.secondaryemail_set.first()

        # Check if the secondary email is now the .be variant
        self.assertEqual(
            secondary_email.email,
            'test@test.be'
        )
