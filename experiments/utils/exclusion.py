from typing import List

from participants.models import Participant
from experiments.models import Experiment


def get_eligible_participants_for_experiment(experiment: Experiment,
                                             on_mailinglist: bool = True) -> \
        List[Participant]:
    """
    This function produces a list of participants that can take part in
    the provided experiment.
    """
    # Base filters: a participant should be capable, and by default be on the
    # mailing list
    filters = {
        'email_subscription': on_mailinglist,
        'capable':            True,
    }

    default_criteria = experiment.defaultcriteria
    specific_criteria = experiment.experimentcriterium_set.all()

    # List of vars that can have the same values as the participant model
    # variables, with an indifferent option
    indifferentable_vars = [
        'language',
        'sex',
        'handedness',
        'social_status',
    ]

    for var in indifferentable_vars:
        if getattr(default_criteria, var) != 'I':
            filters[var] = getattr(default_criteria, var)

    # Dyslexia is always a filter
    expected_value = default_criteria.dyslexia == 'Y'
    filters['dyslexic'] = expected_value

    if default_criteria.multilingual != 'I':
        expected_value = default_criteria.multilingual == 'Y'
        filters['multilingual'] = expected_value

    # We could do this with a different if statement in the loop, but this
    # makes the loop look cleaner
    max_age = default_criteria.max_age
    if max_age == -1:
        max_age = 9000  # we assume no-one is older than 9000 years old....

    # List of all allowed participants
    filtered = []

    # Exclude all participants with an appointment for an experiment that was
    # marked as an exclusion criteria
    excludes = {
        'appointments__timeslot__experiment__in':
            experiment.excluded_experiments.all()
    }
    participants = Participant.objects.exclude(**excludes)

    for participant in participants:
        should_include = True

        # Loop over the defined filters
        for attr, expected_value in filters.items():
            # If we the actual value is not the same as the expected,
            # mark this participant as 'to exclude'
            if getattr(participant, attr) != expected_value:
                should_include = False
                continue

        # Loop over the specific criteria for this experiment
        for specific_criterium in specific_criteria:
            # See if we have an answer for this participant
            answer = specific_criterium.criterium.criteriumanswer_set.filter(
                participant=participant
            )
            if answer:
                # If so, check that answer
                if specific_criterium.correct_value != answer[0].answer:
                    should_include = False
                    continue

        if participant.age < default_criteria.min_age:
            continue

        if participant.age > max_age:
            continue

        if should_include:
            filtered.append(participant)

    return filtered
