from typing import List, Tuple
from datetime import datetime

from datamanagement.utils.common import get_threshold_years_ago
from experiments.models import Experiment


def get_experiments_with_visibility() -> List[Tuple[Experiment, datetime]]:
    out = []
    threshold = get_threshold_years_ago('participant_visibility')

    for experiment in Experiment.objects.filter(
        participants_visible=True,
        timeslot__datetime__lte=threshold,
    ).distinct():
        out.append(
            (experiment, datetime.now())
        )

    return out


def hide_part_from_exp(experiment: Experiment) -> None:
    experiment.participants_visible = False
    experiment.save()
