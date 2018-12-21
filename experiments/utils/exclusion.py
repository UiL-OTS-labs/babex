"""
Note: the functions in this module are heavily optimised to minimize
processing and database accesses. This does mean that the code is not as
straightforward as you'd expect.

Also, because we use application-level database encryption, we cannot compare
inside the database. This is why everything is done in python.
"""
from typing import List
from django.db.models.expressions import RawSQL

from experiments.models import Experiment, ExperimentCriterium
from participants.models import CriteriumAnswer, Participant

# List of vars that can have the same values as the participant model
# variables, with an indifferent option
indifferentable_vars = [
    'language',
    'sex',
    'handedness',
    'social_status',
]


def get_eligible_participants_for_experiment(experiment: Experiment,
                                             on_mailinglist: bool = True) -> \
        List[Participant]:
    """
    This function produces a list of participants that can take part in
    the provided experiment.
    """
    default_criteria = experiment.defaultcriteria
    specific_experiment_criteria = \
        experiment.experimentcriterium_set.select_related(
            'criterium'
        )
    specific_criteria = [x.criterium for x in specific_experiment_criteria]

    # Base filters: a participant should be capable, and by default be on the
    # mailing list
    filters = {
        'email_subscription': on_mailinglist,
        'capable':            True,
    }

    # Build the rest of the filters
    filters = _build_filters(filters, default_criteria)

    # Exclude all participants with an appointment for an experiment that was
    # marked as an exclusion criteria
    participants = Participant.objects.exclude(
        appointments__timeslot__experiment__in=experiment
            .excluded_experiments.all()
    ).exclude(
        appointments__timeslot__experiment=experiment
    ).prefetch_related(
        'secondaryemail_set',
    ).annotate(
        # This is black magic (Read: workaround for a bug in Django 2.0)
        has_invitation=RawSQL("SELECT COUNT(*) AS \"has_invitation\" FROM "
                              "experiments_invitation WHERE experiment_id = "
                              "%s AND participant_id = "
                              "participants_participant.id", (experiment.pk,) )
    )

    # Get all criterium answers for the criteria in this experiment and the
    # participants we're going to filter
    criteria_answers = CriteriumAnswer.objects.select_related(
        'criterium',
        'participant',
    )
    criteria_answers = criteria_answers.filter(
        criterium__in=specific_criteria,
        participant__in=participants
    )

    # Turn our QuerySet into a list, so we can modify it
    criteria_answers = list(criteria_answers)

    # List of all allowed participants
    filtered = []

    for participant in participants:

        if _should_exclude_by_filters(participant, filters):
            continue

        if _should_exclude_by_age(participant, default_criteria):
            continue

        if _should_exclude_by_specific_criteria(participant,
                                                specific_experiment_criteria,
                                                criteria_answers):
            continue

        filtered.append(participant)

    return filtered


def _build_filters(filters: dict, default_criteria) -> dict:
    """
    This function expands a given filter dict with filters as specified in
    the given default_criteria
    :param filters:
    :param default_criteria:
    :return:
    """
    for var in indifferentable_vars:
        if getattr(default_criteria, var) != 'I':
            filters[var] = getattr(default_criteria, var)

    # Dyslexia is always a filter
    expected_value = default_criteria.dyslexia == 'Y'
    filters['dyslexic'] = expected_value

    if default_criteria.multilingual != 'I':
        expected_value = default_criteria.multilingual == 'Y'
        filters['multilingual'] = expected_value

    return filters


def _should_exclude_by_filters(participant: Participant, filters: dict) -> bool:
    """
    Determines if a participant should be excluded based upon a given filter
    dict
    :param participant:
    :param filters:
    :return:
    """
    # Loop over the defined filters
    for attr, expected_value in filters.items():
        # If we the actual value is not the same as the expected,
        # mark this participant as 'to exclude'
        if getattr(participant, attr) != expected_value:
            return True

    return False


def _should_exclude_by_specific_criteria(participant: Participant,
                                         specific_experiment_criteria,
                                         criteria_answers: list) -> bool:
    """
    Determines if a participant should be excluded based upon their
    :param participant:
    :param specific_experiment_criteria:
    :param criteria_answers:
    :return:
    """

    # Loop over all criteria answers
    for specific_criterium_answer in criteria_answers.copy():
        # Check if this answer is by the current participant
        # We do this in python to minimize db queries (it's way faster)
        if not specific_criterium_answer.participant == participant:
            continue

        # Get the experiment criterium
        specific_criterium = _get_specific_criterium(
            specific_experiment_criteria,
            specific_criterium_answer.criterium
        )

        # Remove this answer from our list, in order to shorten this loop in
        # the next call by removing answers we've already evaluated
        criteria_answers.remove(specific_criterium_answer)

        if specific_criterium and not specific_criterium_answer.answer == \
                                      specific_criterium.correct_value:
            return True

    return False


def _get_specific_criterium(specific_experiment_criteria, criterium) -> \
        ExperimentCriterium:
    """
    Gets the experimentCriterium object for a criterium object
    :param specific_experiment_criteria:
    :param criterium:
    :return:
    """
    for x in specific_experiment_criteria:
        if x.criterium == criterium:
            return x


def _should_exclude_by_age(participant: Participant, default_criteria) -> bool:
    """
    Determines if a participant should be excluded based upon their age

    :param participant:
    :param default_criteria:
    :return:
    """
    if participant.age < default_criteria.min_age:
        return True

    # We could do this with a different if statement in the loop, but this
    # makes the loop look cleaner
    max_age = default_criteria.max_age
    if max_age == -1:
        max_age = 9000  # we assume no-one is older than 9000 years old....

    if participant.age > max_age:
        return True

    return False
