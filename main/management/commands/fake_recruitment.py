
from django.core.management.base import BaseCommand, CommandError

from participants.simulate import simulate_recruitment

import datetime as dt


def _positive_int(value):
    intval = int(value)
    if intval < 0:
        raise CommandError(message="Expected value larger than 0")
    return intval


class Command(BaseCommand):
    """
    Allow manage.py to generate participants for debug purposes.
    """
    help = 'Generate participants for testing purposes, NOT for production'

    def add_arguments(self, parser):
        parser.add_argument(
            'year',
            help="The year of the test recruitment",
            type=int
        )
        parser.add_argument(
            'month',
            help="The month of the test recruitment",
            choices=list(range(1, 13)),
            type=int
        )
        parser.add_argument(
            '--day',
            help="The month of the test recruitment",
            type=int,
            default=1
        )
        parser.add_argument(
            "-n", "--number",
            help="The number of participant that are recruited",
            type=_positive_int,
            default=100
        )

    def handle(self, *args, **options):
        """Validates provided arguments"""
        year = options['year']
        month = options['month']
        day = options['day']
        number = options['number']

        date = dt.datetime(year=year, month=month, day=day)

        simulate_recruitment(number, date)
