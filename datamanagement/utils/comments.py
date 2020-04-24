from typing import List, Tuple, Iterable

from datamanagement.utils.common import get_threshold_years_ago
from experiments.models import Experiment
from comments.models import Comment


def get_old_experiments() -> Iterable[Experiment]:
    return Experiment.objects.filter(
        comment__datetime__lte=get_threshold_years_ago('comments')
    ).distinct()


def get_comment_counts() -> List[Tuple[Experiment, int]]:
    out = []

    for experiment in get_old_experiments():
        num = Comment.objects.filter(experiment=experiment).count()

        if num:
            out.append(
                (experiment, num)
            )

    return out


def delete_comments(experiment: Experiment) -> None:
    Comment.objects.filter(experiment=experiment).delete()
