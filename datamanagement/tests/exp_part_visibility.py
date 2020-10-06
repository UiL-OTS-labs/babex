from datetime import datetime, timedelta

from django.test import TestCase
from django.utils.timezone import get_current_timezone

from datamanagement.tests.common import _create_experiment, _create_thresholds
from datamanagement.utils.exp_part_visibility import \
    get_experiments_with_visibility, hide_part_from_exp
from experiments.models import Experiment, TimeSlot


class ParticipantVisibilityTests(TestCase):

    def setUp(self) -> None:
        _create_thresholds()
        self.experiments = []

        for days_offset in range(5, 16):
            experiment = _create_experiment(
                timeslot_dts = [
                    datetime.now(tz=get_current_timezone()) - \
                    timedelta(days=days_offset)
                ]
            )

            self.experiments.append(experiment)

    def test_num_experiment(self):
        """Sanity check, to make sure we have the expected num of experiments"""

        self.assertEqual(Experiment.objects.count(), 11)

    def test_num_warnings(self):
        """Test if we have the expected number of warnings"""

        self.assertEqual(len(get_experiments_with_visibility()), 6)

    def test_visibility_toggle(self):
        """Test if the hide_part_from_exp function functions correctly"""
        self.assertEqual(len(get_experiments_with_visibility()), 6)

        hide_part_from_exp(self.experiments[-1])

        self.assertEqual(len(get_experiments_with_visibility()), 5)
