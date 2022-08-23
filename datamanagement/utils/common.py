from datetime import datetime, timedelta
from functools import lru_cache

from django.db.models import Q
from django.utils import timezone
from typing import Iterable

from datamanagement.models import Thresholds
from experiments.models import Experiment


@lru_cache(None)
def get_thresholds_model() -> Thresholds:
    if Thresholds.objects.count() == 0:
        thresholds = Thresholds()
    else:
        thresholds = Thresholds.objects.first()  # type: ignore

    return thresholds


def get_threshold_years_ago(category: str) -> datetime:
    thresholds = get_thresholds_model()
    value = getattr(thresholds, category)
    return timezone.now() - timedelta(days=value)


def get_old_experiments(category: str) -> Iterable[Experiment]:
    return Experiment.objects.filter(
        Q(timeslot__datetime__lte=get_threshold_years_ago(category)) |
        Q(appointments__creation_date__lte=get_threshold_years_ago(category))
    ).distinct()
