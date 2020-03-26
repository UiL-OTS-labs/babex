from typing import Dict, Tuple

from ..models import Comments as OldComment
from comments.models import Comment as NewComment
from experiments.models import Experiment
from participants.models import Participant


def migrate_comments(
    pp_mappings: Dict[int, Participant],
    exp_mappings:  Dict[int, Experiment]
):
    for old_comment in OldComment.objects.all():

        experiment = exp_mappings[old_comment.experiment_id]  # type: Experiment

        new_comment = NewComment()
        new_comment.participant = pp_mappings[old_comment.participant_id]
        # The old system could only have 1 leader per experiment actually linked
        # So, we just take that from the experiment instead of trying to figure
        # it out from the old comment object.
        new_comment.leader = experiment.leader
        new_comment.experiment = experiment
        new_comment.comment = old_comment.comment

        new_comment.save()