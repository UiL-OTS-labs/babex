from comments.models import Comment
from experiments.models import Experiment
from leaders.models import Leader
from participants.models import Participant


def add_comment(experiment: Experiment,
                participant: Participant,
                leader: Leader,
                comment: str) -> None:
    c = Comment()
    c.experiment = experiment
    c.participant = participant
    c.leader = leader
    c.comment = comment
    c.save()
