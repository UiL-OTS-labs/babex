"""
Note: the functions in this module are heavily optimised to minimize
processing and database accesses. This does mean that the code is not as
straightforward as you'd expect.

Also, because we use application-level database encryption, we cannot compare
inside the database. This is why everything is done in python.
"""
from datetime import datetime, timedelta
from typing import List

from ageutil import age

from experiments.models import Appointment, DefaultCriteria, Experiment
from experiments.models.invite_models import Call
from participants.models import Participant


def get_eligible_participants_for_experiment(experiment: Experiment, on_mailinglist: bool = True) -> List[Participant]:
    """
    This function produces a list of participants that can take part in
    the provided experiment.
    """
    default_criteria = experiment.defaultcriteria

    # Build the rest of the filters
    filters = build_exclusion_filters(default_criteria)

    # Exclude deactivated participants
    participants = Participant.objects.filter(deactivated=None)
    # Exclude all participants with an appointment for an experiment that was
    # marked as an exclusion criteria
    participants = participants.exclude(appointments__experiment__in=experiment.excluded_experiments.all())

    # List of all allowed participants
    filtered = []

    for participant in participants:
        appointments = participant.appointments.all()

        # exclude appointments that didn't happen
        appointments = appointments.exclude(outcome=Appointment.Outcome.NOSHOW).exclude(
            outcome=Appointment.Outcome.CANCELED
        )

        participated_in = appointments.values_list("experiment", flat=True)

        if experiment.pk in participated_in:
            # participant has/had an appointment for this experiment
            continue

        required = experiment.required_experiments.values_list("pk", flat=True)
        if not set(required).issubset(participated_in):
            # missing a required experiment
            continue

        if check_default_criteria(participant, filters):
            continue

        if should_exclude_by_age(participant, default_criteria):
            continue

        if should_exclude_by_call_status(participant, experiment):
            continue

        filtered.append(participant)

    return filtered


def check_participant_eligible(experiment: Experiment, participant: Participant) -> bool:
    """
    This function checks if a given participant can participate in a given
    experiment
    """

    default_criteria = experiment.defaultcriteria
    filters = build_exclusion_filters(default_criteria)

    if check_default_criteria(participant, filters):
        return False

    if should_exclude_by_age(participant, default_criteria):
        return False

    return True


def build_exclusion_filters(default_criteria, filters=None) -> dict:
    """
    This function expands a given filter dict with filters as specified in
    the given default_criteria
    :param filters:
    :param default_criteria:
    :return:
    """
    if filters is None:
        filters = {}

    for field in ["sex", "birth_weight", "pregnancy_duration", "multilingual"]:
        value = getattr(default_criteria, field)
        if value is not None:
            filters[field] = set(value)

    for field in ["dyslexic_parent", "tos_parent"]:
        value = getattr(default_criteria, field)
        str_to_bool = {"Y": True, "N": False}
        if value is not None:
            filters[field + "_bool"] = set(str_to_bool[v] for v in value)

    return filters


def check_default_criteria(participant: Participant, filters: dict) -> list:
    """
    Determines if a participant should be excluded based upon a given filter
    dict
    :param participant:
    :param filters:
    :return:
    """
    failed_criteria = []

    # Loop over the defined filters
    for attr, expected_value in filters.items():
        found_value = getattr(participant, attr, None)

        if found_value not in expected_value:
            failed_criteria.append(attr)

    return failed_criteria


def should_exclude_by_age(participant: Participant, criteria: DefaultCriteria) -> bool:
    """
    Determines if a participant should be excluded (from being invited) based upon their age

    :param participant:
    :param default_criteria:
    :return:
    """

    age_pred = age(months=criteria.min_age_months, days=criteria.min_age_days).to(
        months=criteria.max_age_months, days=criteria.max_age_days
    )

    can_participate_today = age_pred.check(participant.birth_date)
    can_participate_within_14_days = age_pred.on(datetime.today() + timedelta(days=14)).check(participant.birth_date)
    return not (can_participate_today or can_participate_within_14_days)


def should_exclude_by_call_status(participant: Participant, experiment: Experiment) -> bool:
    """
    When a parent indicates they cannot participate, there should be a Call object
    for the relevant participant and experiment, with an EXCLUDE status
    """
    return participant.call_set.filter(experiment=experiment, status=Call.CallStatus.EXCLUDE).exists()
