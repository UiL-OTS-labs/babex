from typing import List, Tuple

from auditlog.utils.log import log as log_to_auditlog
from auditlog.enums import Event, UserType
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


def delete_invites(experiment: Experiment, user) -> None:
    log_to_auditlog(
        Event.DELETE_DATA,
        "Deleted invites for experiment '{}'".format(experiment),
        user,
        UserType.ADMIN,
    )

    Invitation.objects.filter(experiment=experiment).delete()
