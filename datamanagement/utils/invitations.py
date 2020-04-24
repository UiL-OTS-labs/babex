from typing import List, Tuple

from datamanagement.utils.common import get_old_experiments
from experiments.models import Experiment, Invitation


def get_invite_counts() -> List[Tuple[Experiment, int]]:
    out = []

    for experiment in get_old_experiments('invites'):
        num = Invitation.objects.filter(experiment=experiment).count()

        if num:
            out.append(
                (experiment, num)
            )

    return out


def delete_invites(experiment: Experiment) -> None:
    Invitation.objects.filter(experiment=experiment).delete()