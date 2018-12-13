from django.test import TestCase
from datetime import datetime
import pytz

from experiments.models import Appointment, Experiment, TimeSlot
from .models import Participant, CriteriumAnswer, SecondaryEmail, Criterium
from .utils import merge_participants


class MergeParticipantsTest(TestCase):

    def setUp(self):
        """
        For these testcases we want 2 participants to merge, plus a few criteria
        """
        self.c1 = Criterium.objects.create(
            name_form='test',
            name_natural='test',
            values='yes,no,maybe',
        )

        self.c2 = Criterium.objects.create(
            name_form='test 2',
            name_natural='test 2',
            values='yes,no,maybe',
        )

        self.c3 = Criterium.objects.create(
            name_form='test 3',
            name_natural='test 3',
            values='yes,no,maybe',
        )

        self.old = Participant.objects.create(
            name='old',
            email='text@test.test',
            phonenumber='123456',
            # required for the model
            dyslexic=False,
            language='nl',
            social_status='student',
        )

        self.new = Participant.objects.create(
            name='new',
            email='text@test.test2',
            phonenumber='654321',
            # required for the model
            dyslexic=False,
            language='nl'
        )

        self.e1 = Experiment.objects.create(
            name='Test experiment 1'
        )

        self.t1 = TimeSlot.objects.create(
            max_places=2,
            experiment=self.e1,
            datetime=datetime(year=1970, month=1, day=1, hour=12, minute=0,
                              tzinfo=pytz.utc),
        )

    def test_basic_merge(self):
        """
        This test case checks the merging of plain attributes
        """
        merge_participants(self.old, self.new)

        # Check basic attribute merge
        self.assertEqual(self.old.name, 'new')
        self.assertEqual(self.old.phonenumber, '654321')
        self.assertEqual(self.old.social_status, None)

        # We should have one secondary email
        self.assertEqual(self.old.secondaryemail_set.count(), 1)

        # We should only have self.new
        self.assertEqual(Participant.objects.count(), 1)

    def test_criterium_merge(self):
        """
        This test case checks if criteria answers are merged properly.
        """

        # old only
        CriteriumAnswer.objects.create(
            criterium=self.c1,
            participant=self.old,
            answer='yes'
        )

        # new and old
        CriteriumAnswer.objects.create(
            criterium=self.c2,
            participant=self.old,
            answer='yes'
        )
        CriteriumAnswer.objects.create(
            criterium=self.c2,
            participant=self.new,
            answer='no'
        )

        # new only
        CriteriumAnswer.objects.create(
            criterium=self.c3,
            participant=self.new,
            answer='maybe'
        )

        # In the beginning, there were 2 answers in self.old and self.new
        self.assertEqual(self.old.criteriumanswer_set.count(), 2)
        self.assertEqual(self.new.criteriumanswer_set.count(), 2)

        # Do the merge!
        merge_participants(self.old, self.new)

        # We should have 3 answers
        self.assertEqual(self.old.criteriumanswer_set.count(), 3)

        # The answer for c2, c3 should've gotten the value from self.new
        self.assertEqual(self.old.criteriumanswer_set.get(
            criterium=self.c2).answer, 'no')
        self.assertEqual(self.old.criteriumanswer_set.get(
            criterium=self.c3).answer, 'maybe')

        # There should only be 3 objects left, as self.new has been deleted
        self.assertEqual(CriteriumAnswer.objects.count(), 3)

    def test_email_merge(self):
        """
        This test case tests if emails are merged correctly
        """

        # old only
        SecondaryEmail.objects.create(
            email='blaat@blaat.nl',
            participant=self.old
        )

        # new only
        SecondaryEmail.objects.create(
            email='bleep@beep.boop',
            participant=self.new
        )

        # both
        SecondaryEmail.objects.create(
            email='WHAT@IS.HAPPENING',
            participant=self.old
        )

        SecondaryEmail.objects.create(
            email='WHAT@IS.HAPPENING',
            participant=self.new
        )

        # Both participants should have 2 secondary emails
        self.assertEqual(self.old.secondaryemail_set.count(), 2)
        self.assertEqual(self.new.secondaryemail_set.count(), 2)

        # Merge old and new
        merge_participants(self.old, self.new)

        # self.old should have 4 secondary emails, 3 we created + the primary
        # email from self.new
        self.assertEqual(self.old.secondaryemail_set.count(), 4)

    def test_experiments_merge(self):
        """
        This test case tests if appointments are merged correctly
        """

        Appointment.objects.create(
            participant=self.old,
            timeslot=self.t1
        )

        Appointment.objects.create(
            participant=self.new,
            timeslot=self.t1,
        )

        self.assertEqual(self.old.appointments.count(), 1)

        merge_participants(self.old, self.new)

        self.assertEqual(self.old.appointments.count(), 2)
