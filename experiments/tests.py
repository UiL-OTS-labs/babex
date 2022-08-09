from datetime import datetime

from pytz import timezone
from dateutil.relativedelta import relativedelta
from django.test import TestCase

from api.auth.models import ApiUser
from leaders.models import Leader
from participants.models import Participant, CriterionAnswer
from .models import Experiment, Criterion, ExperimentCriterion, Appointment, \
    Location, TimeSlot
from .utils.exclusion import get_eligible_participants_for_experiment


def _get_or_create_leader() -> Leader:
    if Leader.objects.exists():
        return Leader.objects.first()
    user = ApiUser.objects.create()
    return Leader.objects.create(api_user=user)


def _get_or_create_location() -> Location:
    if Location.objects.exists():
        return Location.objects.first()
    return Location.objects.create(name="Cyberspace")


class ExclusionTests(TestCase):

    def setUp(self):
        self.experiment = Experiment.objects.create(
            name='test',
            leader=_get_or_create_leader(),
            location=_get_or_create_location(),
        )
        self.experiment.defaultcriteria.language = 'I'
        self.experiment.defaultcriteria.multilingual = 'I'
        self.experiment.defaultcriteria.save()

        self.excluded_experiment = Experiment.objects.create(
            name='excluded'
        )

        self.time_slot = TimeSlot.objects.create(
            experiment=self.excluded_experiment,
            datetime=datetime.now(tz=timezone('UTC')),
            max_places=9000,
        )

        self.criterion = Criterion.objects.create(
            name_form='test',
            name_natural='test',
            values='yes,no',
        )

        i = 0

        self.dt_18 = datetime.now() - relativedelta(years=18)
        self.dt_20 = datetime.now() - relativedelta(years=20)
        self.dt_30 = datetime.now() - relativedelta(years=30)

        # We have less dyslexics to simulate real life (and the first two tests
        # are equal otherwise)
        self.dyslexic_options = [True, False, False]
        self.age_options = [self.dt_18, self.dt_20, self.dt_30, None]
        self.multilingual_options = [True, False, None]
        self.language_options = ['nl', 'Elvish']
        self.sex_options = ['M', 'F', None]
        self.criterion_answers_options = ['yes', 'no']
        self.excluded_experiment_options = [False, True]

        for dyslexic_parent in self.dyslexic_options:
            for age in self.age_options:
                for multilingual in self.multilingual_options:
                    for language in self.language_options:
                        for sex in self.sex_options:
                            for criterion_answer in \
                                    self.criterion_answers_options:
                                for excluded_experiment in \
                                        self.excluded_experiment_options:
                                    p = Participant.objects.create(
                                        name="test {}".format(i),
                                        dyslexic_parent=dyslexic_parent,
                                        birth_date=age,
                                        multilingual=multilingual,
                                        language=language,
                                        sex=sex,
                                        email_subscription=True,
                                    )

                                    CriterionAnswer.objects.create(
                                        participant=p,
                                        criterion=self.criterion,
                                        answer=criterion_answer,
                                    )

                                    if excluded_experiment:
                                        Appointment.objects.create(
                                            participant=p,
                                            timeslot=self.time_slot,
                                            experiment=self.excluded_experiment,
                                        )

                                    i += 1

    @property
    def num_options(self):
        return len(self.multilingual_options) * len(self.age_options) * \
               len(self.language_options) * len(self.sex_options) * \
               len(self.criterion_answers_options) * \
               len(self.excluded_experiment_options)

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

        self._remove_options('dyslexic_parent', True)

        self.assertEqual(self.num_options, len(part))

    def test_exclude_non_dyslectics(self):
        """Exclude non dyslectics"""
        # Override the default value for language
        self.experiment.defaultcriteria.dyslexia = 'Y'

        part = get_eligible_participants_for_experiment(self.experiment)

        self._remove_options('dyslexic_parent', False)
        self.assertEqual(self.num_options, len(part))

    def test_exclude_min_age(self):
        self.experiment.defaultcriteria.min_age = 19

        part = get_eligible_participants_for_experiment(self.experiment)

        self._remove_options('age', self.dt_18)
        self._remove_options('dyslexic_parent', True)
        self.assertEqual(self.num_options, len(part))

    def test_exclude_max_age(self):
        self.experiment.defaultcriteria.max_age = 25

        part = get_eligible_participants_for_experiment(self.experiment)

        self._remove_options('age', self.dt_30)
        self._remove_options('dyslexic_parent', True)
        self.assertEqual(self.num_options, len(part))

    def test_exclude_min_max_age(self):
        self.experiment.defaultcriteria.min_age = 19
        self.experiment.defaultcriteria.max_age = 25

        part = get_eligible_participants_for_experiment(self.experiment)

        self._leave_options('age', [self.dt_20, None])
        self._remove_options('dyslexic_parent', True)
        self.assertEqual(self.num_options, len(part))

    def test_exclude_multilinguals(self):
        self.experiment.defaultcriteria.multilingual = 'N'

        part = get_eligible_participants_for_experiment(self.experiment)
        self._remove_options('dyslexic_parent', True)
        self._leave_options('multilingual', [False, None])
        self.assertEqual(self.num_options, len(part))

    def test_exclude_singlelinguals(self):
        self.experiment.defaultcriteria.multilingual = 'Y'

        part = get_eligible_participants_for_experiment(self.experiment)

        self._remove_options('dyslexic_parent', True)
        self._leave_options('multilingual', [True, None])
        self.assertEqual(self.num_options, len(part))

    def test_exclude_elvish(self):
        self.experiment.defaultcriteria.language = 'nl'

        part = get_eligible_participants_for_experiment(self.experiment)

        self._remove_options('dyslexic_parent', True)
        self._leave_options('language', 'nl')
        self.assertEqual(self.num_options, len(part))

    def test_exclude_dutch(self):
        self.experiment.defaultcriteria.language = 'Elvish'

        part = get_eligible_participants_for_experiment(self.experiment)

        self._remove_options('dyslexic_parent', True)
        self._leave_options('language', 'Elvish')
        self.assertEqual(self.num_options, len(part))

    def test_exclude_males(self):
        self.experiment.defaultcriteria.sex = 'F'

        part = get_eligible_participants_for_experiment(self.experiment)

        self._remove_options('dyslexic_parent', True)
        self._leave_options('sex', ['F', None])
        self.assertEqual(self.num_options, len(part))

    def test_exclude_females(self):
        self.experiment.defaultcriteria.sex = 'M'

        part = get_eligible_participants_for_experiment(self.experiment)

        self._remove_options('dyslexic_parent', True)
        self._leave_options('sex', ['M', None])
        self.assertEqual(self.num_options, len(part))

    def test_specific_criteria_exclusion(self):
        ExperimentCriterion.objects.create(
            experiment=self.experiment,
            criterion=self.criterion,
            correct_value='yes'
        )

        part = get_eligible_participants_for_experiment(self.experiment)

        self._leave_options('criterion_answers', 'yes')
        self._remove_options('dyslexic_parent', True)
        self.assertEqual(self.num_options, len(part))

    def test_experiment_exclusion(self):
        self.experiment.excluded_experiments.add(self.excluded_experiment)

        part = get_eligible_participants_for_experiment(self.experiment)

        self._remove_options('dyslexic_parent', True)
        self._leave_options('excluded_experiment', False)
        self.assertEqual(self.num_options, len(part))

    def test_exclude_already_subscribed(self):
        # Do a manual filter, because encrypted fields don't like filters
        participants = Participant.objects.all()
        participants = [participant for participant in participants if not
                        participant.dyslexic_parent]

        time_slot = TimeSlot.objects.create(
            experiment=self.experiment,
            datetime=datetime.now(tz=timezone('UTC')),
            max_places=9000,
        )

        # Add half the participants to the timeslot
        for participant in participants[:len(participants)//2]:
            Appointment.objects.create(
                timeslot=time_slot,
                participant=participant,
                experiment=self.experiment,
            )

        part = get_eligible_participants_for_experiment(self.experiment)

        self._remove_options('dyslexic_parent', True)
        # manually calculate half of num_options
        self.assertEqual(self.num_options//2, len(part))
