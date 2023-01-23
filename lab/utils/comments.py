from comments.models import Comment
from experiments.models import Experiment
from main.models import User
from participants.models import Participant


def add_comment(experiment: Experiment,
                participant: Participant,
                leader: User,
                comment: str) -> None:
    c = Comment()
    c.participant = participant
    c.leader = leader
    c.comment = comment
    c.save()
