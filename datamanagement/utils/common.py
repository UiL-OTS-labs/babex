from datetime import datetime, timedelta

from django.utils import timezone
from typing import Iterable

from experiments.models import Experiment


def get_threshold_years_ago() -> datetime:
    return timezone.now() - timedelta(days=1 * 365)


def get_old_experiments() -> Iterable[Experiment]:
    return Experiment.objects.filter(
        timeslot__datetime__lte=get_threshold_years_ago()
    ).distinct()
