from functools import reduce
from operator import iconcat
from typing import List

from django.db.models import QuerySet

from experiments.utils.exclusion import get_eligible_participants_for_experiment
from main.models import User

from .models import Participant


def participants_visible_to_leader(leader: User) -> QuerySet[Participant]:
    # look at experiments that leader has access to, and return only participants
    # that have participated, or are eligible for participation in those experiments
    experiments = leader.experiments.all().values_list("pk", flat=True)
    participants = Participant.objects.filter(appointments__experiment__in=experiments)

    eligible = [get_eligible_participants_for_experiment(experiment) for experiment in leader.experiments.all()]
    # flatten list of lists
    flat: List[Participant] = reduce(iconcat, eligible, [])
    # extract ids
    participants |= Participant.objects.filter(pk__in=[participant.pk for participant in flat])

    return participants.distinct()


def can_leader_access_participant(leader: User, participant: Participant) -> bool:
    # not very efficient, but ok for now
    return leader.is_staff or participant in participants_visible_to_leader(leader)
