from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.test import TestCase

from participants.models import Participant
from .models import Experiment
from .utils.exclusion import get_eligible_participants_for_experiment


class ExclusionTests(TestCase):

    def setUp(self):
        self.experiment = Experiment.objects.create(
            name='test'
        )
        self.experiment.defaultcriteria.language = 'I'
        self.experiment.defaultcriteria.save()

        i = 0

        dt_18 = datetime.now() - relativedelta(years=18)
        dt_20 = datetime.now() - relativedelta(years=20)
        dt_30 = datetime.now() - relativedelta(years=30)

        # We have less dyslexics to simulate real life (and the first two tests
        # are equal otherwise)
        self.dyslexic_options = [True, False, False]
        self.age_options = [dt_18, dt_20, dt_30]
        self.multilingual_options = [True, False]
        self.handedness_options = ['L', 'R']
        self.language_options = ['nl', 'Elvish']
        self.sex_options = ['M', 'F']
        self.social_status_options = ['S', 'O']

        # TODO: Add experiment exclusion tests
        # TODO: Add specific criteria exclusion tests

        for dyslexic in self.dyslexic_options:
            for age in self.age_options:
                for multilingual in self.multilingual_options:
                    for handedness in self.handedness_options:
                        for language in self.language_options:
                            for sex in self.sex_options:
                                for social_status in self.social_status_options:
                                    Participant.objects.create(
                                        name="test {}".format(i),
                                        dyslexic=dyslexic,
                                        birth_date=age,
                                        multilingual=multilingual,
                                        handedness=handedness,
                                        language=language,
                                        sex=sex,
                                        social_status=social_status,
                                        email_subscription=True,
                                    )
                                    i += 1

    @property
    def num_options(self):
        return len(self.handedness_options) * \
               len(self.multilingual_options) * len(self.age_options) * \
               len(self.language_options) * len(self.sex_options) * \
               len(self.social_status_options) * len(self.dyslexic_options)

    def _remove_options(self, name, values):
        name = "{}_options".format(name)
        options = getattr(self, name)

        if isinstance(values, list):
            setattr(
                self,
                name,
                [x for x in options if x not in values]
            )
        else:
            setattr(
                self,
                name,
                [x for x in options if x != values]
            )

    def _leave_options(self, name, values):
        name = "{}_options".format(name)
        options = getattr(self, name)

        if isinstance(values, list):
            setattr(
                self,
                name,
                [x for x in options if x  in values]
            )
        else:
            setattr(
                self,
                name,
                [x for x in options if x == values]
            )

    def test_exclude_none(self):
        """Exclude only dyslectics (the default)"""
        # Override the default value for language
        part = get_eligible_participants_for_experiment(self.experiment)

        self._remove_options('dyslexic', True)

        self.assertEqual(self.num_options, len(part))

    def test_exclude_non_dyslectics(self):
        """Exclude non dyslectics"""
        # Override the default value for language
        self.experiment.defaultcriteria.dyslexia = 'Y'

        part = get_eligible_participants_for_experiment(self.experiment)

        self._remove_options('dyslexic', False)
        self.assertEqual(self.num_options, len(part))

    def test_exclude_min_age(self):
        self.experiment.defaultcriteria.min_age = 19

        part = get_eligible_participants_for_experiment(self.experiment)

        num_options = len(self.handedness_options) * \
                      len(self.multilingual_options) * 2 * \
                      len(self.language_options) * len(self.sex_options) * \
                      len(self.social_status_options) * 2

        self.assertEqual(num_options, len(part))

    def test_exclude_max_age(self):
        self.experiment.defaultcriteria.max_age = 25
        part = get_eligible_participants_for_experiment(self.experiment)

        num_options = len(self.handedness_options) * \
                      len(self.multilingual_options) * 2 * \
                      len(self.language_options) * len(self.sex_options) * \
                      len(self.social_status_options) * 2

        self.assertEqual(num_options, len(part))

    def test_exclude_min_max_age(self):
        self.experiment.defaultcriteria.min_age = 19
        self.experiment.defaultcriteria.max_age = 25
        part = get_eligible_participants_for_experiment(self.experiment)

        num_options = len(self.handedness_options) * \
                      len(self.multilingual_options) * 1 * \
                      len(self.language_options) * len(self.sex_options) * \
                      len(self.social_status_options) * 2

        self.assertEqual(num_options, len(part))

    def test_exclude_right_handed(self):
        self.experiment.defaultcriteria.handedness = 'L'

        part = get_eligible_participants_for_experiment(self.experiment)

        self._remove_options('dyslexic', True)
        self._remove_options('handedness', 'R')
        self.assertEqual(self.num_options, len(part))

    def test_exclude_left_handed(self):
        self.experiment.defaultcriteria.handedness = 'R'

        part = get_eligible_participants_for_experiment(self.experiment)

        self._remove_options('dyslexic', True)
        self._remove_options('handedness', 'L')
        self.assertEqual(self.num_options, len(part))

    def test_exclude_multilinguals(self):
        self.experiment.defaultcriteria.multilingual = 'N'

        part = get_eligible_participants_for_experiment(self.experiment)
        self._remove_options('dyslexic', True)
        self._leave_options('multilingual', False)
        self.assertEqual(self.num_options, len(part))

    def test_exclude_singlelinguals(self):
        self.experiment.defaultcriteria.multilingual = 'Y'

        part = get_eligible_participants_for_experiment(self.experiment)

        self._remove_options('dyslexic', True)
        self._leave_options('multilingual', True)
        self.assertEqual(self.num_options, len(part))

    def test_exclude_elvish(self):
        self.experiment.defaultcriteria.language = 'nl'

        part = get_eligible_participants_for_experiment(self.experiment)

        self._remove_options('dyslexic', True)
        self._leave_options('language', 'nl')
        self.assertEqual(self.num_options, len(part))

    def test_exclude_dutch(self):
        self.experiment.defaultcriteria.language = 'Elvish'

        part = get_eligible_participants_for_experiment(self.experiment)

        self._remove_options('dyslexic', True)
        self._leave_options('language', 'Elvish')
        self.assertEqual(self.num_options, len(part))

    def test_exclude_males(self):
        self.experiment.defaultcriteria.sex = 'F'

        part = get_eligible_participants_for_experiment(self.experiment)

        self._remove_options('dyslexic', True)
        self._leave_options('sex', 'F')
        self.assertEqual(self.num_options, len(part))

    def test_exclude_females(self):
        self.experiment.defaultcriteria.sex = 'M'

        part = get_eligible_participants_for_experiment(self.experiment)

        self._remove_options('dyslexic', True)
        self._leave_options('sex', 'M')
        self.assertEqual(self.num_options, len(part))

    def test_exclude_students(self):
        self.experiment.defaultcriteria.social_status = 'S'

        part = get_eligible_participants_for_experiment(self.experiment)

        self._remove_options('dyslexic', True)
        self._leave_options('social_status', 'S')
        self.assertEqual(self.num_options, len(part))

    def test_exclude_others(self):
        self.experiment.defaultcriteria.social_status = 'O'

        part = get_eligible_participants_for_experiment(self.experiment)

        self._remove_options('dyslexic', True)
        self._leave_options('social_status', 'O')
        self.assertEqual(self.num_options, len(part))