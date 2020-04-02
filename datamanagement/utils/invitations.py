from typing import List, Tuple

from experiments.models import Experiment, Invitation

def get_invite_counts() -> List[Tuple[Experiment, int]]:
    out = []

    for experiment in Experiment.objects.all():
        num = Invitation.objects.filter(experiment=experiment).count()

        if num:
            out.append(
                (experiment, num)
            )

    return out
