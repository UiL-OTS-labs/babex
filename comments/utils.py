from typing import Union, List

from comments.models import Comment
from participants.models import Participant


def add_system_comment(
        participants: Union[List[Participant], Participant],
        comment: str,
        experiment = None
) -> None:
    """
    Adds a system comment for a given participant or a list of participant.

    If multiple participants are given, the comment will be the same for all
    of them.

    :param participants: Either a single Participant object or a list of them
    :param comment: the comment to add.
    """

    if not isinstance(participants, list):
        participants = [participants]

    for participant in participants:
        c = Comment()
        c.participant = participant
        c.experiment = experiment
        c.comment = comment
        c.system_comment = True
        c.save()
