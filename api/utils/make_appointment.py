from typing import List, Tuple

from django.core.exceptions import ObjectDoesNotExist, SuspiciousOperation
from django.core.validators import ValidationError, validate_email
from django.utils.dateparse import parse_date

from comments.models import Comment
from experiments.models import Appointment, DefaultCriteria, Experiment, \
    TimeSlot
from experiments.utils.exclusion import indifferentable_vars
from main.utils import get_supreme_admin
from participants.models import Participant
from .common import x_or_else

DEFAULT_INVALID_MESSAGES = {
    'language':         'Je kunt niet meedoen met het experiment omdat je '
                        'moedertaal niet overeen komt met de criteria voor '
                        'dit experiment. Als je denkt dat dit niet klopt, '
                        'neem dan even contact op met {}',

    'multilingual_yes': 'Je kunt niet meedoen met het experiment omdat je '
                        'niet meertalig bent. Om mee te doen aan dit '
                        'experiment moet je meertalig zijn. Als je denkt dat '
                        'dit niet klopt, neem dan even contact op met {}',
    'multilingual_no':  'Je kunt niet meedoen met het experiment omdat je '
                        'meertalig bent. Om mee te doen aan dit experiment '
                        'mag je niet meertalig zijn. Als je denkt dat '
                        'dit niet klopt, neem dan even contact op met {}',
    'sex':              'Je kunt niet meedoen met het experiment omdat je '
                        'geslacht niet overeen komt met de criteria voor '
                        'dit experiment. Als je denkt dat dit niet klopt, '
                        'neem dan even contact op met {}',
    'handedness':       'Je kunt niet meedoen met het experiment omdat je '
                        'voorkeurshand niet overeen komt met de criteria voor '
                        'dit experiment. Als je denkt dat dit niet klopt, '
                        'neem dan even contact op met {}',
    'age':              'Je kunt niet meedoen met het experiment omdat je '
                        'leeftijd niet overeen komt met de criteria voor '
                        'dit experiment. Als je denkt dat dit niet klopt, '
                        'neem dan even contact op met {}',
    'dyslexic_yes':     'Je kunt niet meedoen met het experiment omdat je '
                        'volgens onze gegevens niet dyslectisch bent.  Als je '
                        'denkt dat dit niet klopt, neem dan even contact op '
                        'met {}',
    'dyslexic_no':      'Je kunt niet meedoen met het experiment omdat je '
                        'volgens onze gegevens dyslectisch bent. Als je denkt '
                        'dat dit niet klopt, neem dan even contact op met {}',
    'social_status_S':  'Je kunt niet meedoen met het experiment omdat je '
                        'volgens onze gegevens niet student bent. Als je '
                        'denkt dat dit niet klopt, neem dan even contact op '
                        'met {}',
    'social_status_O':  'Je kunt niet meedoen met het experiment omdat je '
                        'volgens onze gegevens student bent. Als je denkt '
                        'dat dit niet klopt, neem dan even contact op met {}',
}

MISC_INVALID_MESSAGES = {
    'email':    "Je hebt geen geldig email adres ingevuld! Probeer opnieuw.",
    'timeslot': "Aanmelding mislukt: sorry, dit tijdstip is al door iemand "
                "anders gereserveerd! Probeer opnieuw."
}

INVALID_EXPERIMENT_MESSAGE = "Je hebt al meegedaan met een eerdere versie " \
                             "van dit experiment en kunt helaas niet nog een" \
                             " keer meedoen. Dankjewel voor je belangstelling!"


def register_participant(data: dict, experiment: Experiment) -> Tuple[bool,
                                                                      bool,
                                                                      list]:
    default_criteria = experiment.defaultcriteria

    try:
        time_slot = experiment.timeslot_set.get(pk=data.get('timeslot'))
    except TimeSlot.DoesNotExist:
        time_slot = None

    participant = _get_participant(data)

    invalid_default_criteria, \
    default_criteria_messages = _handle_default_criteria(
        default_criteria,
        participant
    )

    invalid_specific_criteria, \
    specific_criteria_messages = _handle_specific_criteria(
        experiment,
        data,
        participant
    )

    invalid_previous_experiments, \
    experiment_messages = _handle_excluded_experiments(
        experiment,
        participant
    )

    invalid_misc_items, \
    misc_messages = _handle_misc_items(
        data,
        time_slot,
    )

    success = not invalid_default_criteria and not invalid_specific_criteria \
              and not invalid_previous_experiments and not invalid_misc_items

    if success:
        participant.save()
        _make_appointment(participant, time_slot)

        # We set recoverable to false, as there is nothing to recover
        # Also, it's easier to work with in the client's view
        return success, False, ["Je bent ingeschreven voor het experiment! "
                                "Je krijgt een bevestiging per email."]

    recoverable = not invalid_default_criteria and not \
        invalid_specific_criteria and not invalid_previous_experiments

    # Else, get human-friendly messages and return the whole thing
    messages = _format_messages(
        default_criteria_messages,
        specific_criteria_messages,
        experiment_messages,
        misc_messages,
    )

    # Success, recoverable, messages
    return success, recoverable, messages


def get_required_fields(experiment: Experiment, participant: Participant):
    fields = []

    for field in experiment.defaultcriteria.__dict__.keys():
        if field not in ['experiment', 'experiment_id', 'min_age', 'max_age',
                         'dyslexia', '_state']:
            if getattr(participant, field) is None:
                fields.append(field)

    for field in ['birth_date', 'phonenumber', 'name']:
        if getattr(participant, field) is None:
            fields.append(field)

    if participant.dyslexic is None:
        fields.append('dyslexia')

    answers = participant.criterionanswer_set.all()

    for experiment_criterion in experiment.experimentcriterion_set.all():
        try:
            answers.get(criterion=experiment_criterion.criterion)
        except ObjectDoesNotExist:
            fields.append(experiment_criterion.criterion.name_form)

    return fields


def _get_participant(data: dict) -> Participant:
    to_lower = lambda x: str(x).lower()

    email = data.get('email')

    participants = [x for x in
                    Participant.objects.prefetch_related(
                        'secondaryemail_set'
                    ) if
                    to_lower(x.email) == email or
                    email in [to_lower(y.email) for y in
                              x.secondaryemail_set.all()]
                    ]

    # If we have a participant, get the first one that matches
    if len(participants) > 0:
        participant = participants[0]
    else:
        # If not, create a new one
        participant = Participant()
        participant.email = email

    # These variables aren't allowed to be changed by the participant
    # (And most shouldn't be able to change irl, unless a cure for
    # dyslexia has been developed. In which case, please do tell)
    # However, we might not know them yet. x_or_else will keep the existing
    # data, but if the existing data is None it will update with the given data.
    participant.name = x_or_else(
        participant.name,
        data.get('name')
    )

    participant.multilingual = x_or_else(
        participant.multilingual,
        data.get('multilingual') == 'Y'
    )

    participant.language = x_or_else(
        participant.language,
        data.get('language')
    )

    participant.handedness = x_or_else(
        participant.handedness,
        data.get('handedness')
    )

    participant.sex = x_or_else(
        participant.sex,
        data.get('sex')
    )

    participant.birth_date = x_or_else(
        participant.birth_date,
        parse_date(data.get('birth_date'))
    )
    participant.dyslexic = x_or_else(
        participant.dyslexic,
        data.get('dyslexic') == 'Y'
    )

    # Update/set all variables that can be changed
    participant.social_status = data.get('social_status')
    participant.phone = data.get('phone')
    if 'mailinglist' in data:
        participant.email_subscription = data.get('mailinglist')

    return participant


def _handle_default_criteria(
        default_criteria: DefaultCriteria,
        participant: Participant,
) -> Tuple[list, list]:
    filters = {}
    messages = []

    for var in indifferentable_vars:
        if getattr(default_criteria, var) != 'I':
            filters[var] = getattr(default_criteria, var)

    # Dyslexia is always a filter
    expected_value = default_criteria.dyslexia == 'Y'
    filters['dyslexic'] = expected_value

    if default_criteria.multilingual != 'I':
        expected_value = default_criteria.multilingual == 'Y'
        filters['multilingual'] = expected_value

    failed_criteria = []

    for attr, expected_value in filters.items():
        value = getattr(participant, attr)

        # If we are going to compare strings, let's make sure we compare
        # lowercase, stripped strings.
        if isinstance(value, str):
            value = value.lower().strip()
            expected_value = expected_value.lower().strip()

        # If we the actual value is not the same as the expected,
        # add the field to a list of failed criteria.
        if value != expected_value:
            failed_criteria.append(attr)

            # These fields have different error messages depending on the
            # expected value
            if attr in ['multilingual', 'dyslexic', 'social_status']:

                # Map booleans to yes,no
                if isinstance(expected_value, bool):
                    if expected_value:
                        specifier = 'yes'
                    else:
                        specifier = 'no'
                else:
                    # Otherwise, just use the value
                    specifier = expected_value

                # Make the right key
                message_key = "{}_{}".format(attr, specifier)

                messages.append(
                    DEFAULT_INVALID_MESSAGES[message_key]
                )
            else:
                messages.append(DEFAULT_INVALID_MESSAGES[attr])

    if participant.age < default_criteria.min_age:
        failed_criteria.append('age')
        messages.append(DEFAULT_INVALID_MESSAGES['age'])
    # Check if the participant is older than the max age, and max age is
    # bigger than -1 (the special value indicating 'no max age')
    elif participant.age > default_criteria.max_age > -1:
        failed_criteria.append('age')
        messages.append(DEFAULT_INVALID_MESSAGES['age'])

    return failed_criteria, messages


def _handle_specific_criteria(
        experiment: Experiment,
        data: dict,
        participant: Participant
) -> Tuple[list, list]:
    specific_criteria = experiment.experimentcriterion_set.all()
    failed_criteria = []
    messages = []

    # Check if we have specific criteria in our data, if not: fail all fields
    if 'specific_criteria' not in data or not data['specific_criteria']:
        for specific_criterion in specific_criteria:
            failed_criteria.append(specific_criterion.criterion.name_form)
            messages.append(specific_criterion.message_failed)

        return failed_criteria, messages

    try:
        # Rewrite the list of dicts back into a dict of field: value
        data = {x['name']: int(x['value']) for x in data['specific_criteria']}
    except ValueError:
        # ValueError means the user is submitting weird data. This should not
        # happen, but just in case we are going to crash Django in a secure
        # manner
        raise SuspiciousOperation

    for specific_criterion in specific_criteria:
        name_form = specific_criterion.criterion.name_form

        if name_form not in data:
            failed_criteria.append(
                name_form
            )
            continue

        value = data.get(name_form)
        # The value sent is actually an integer index corresponding to a value
        # in values_list, so we extract the chosen value from that list.
        value = specific_criterion.criterion.values_list[value]

        if specific_criterion.correct_value != value:
            failed_criteria.append(name_form)

        answer = participant.criterionanswer_set.filter(
            criterion=specific_criterion.criterion
        ).first()

        if answer:
            # Check if the value answered conflicts with the answer this
            # participant has already given (if that previous answer exists)
            if answer.answer != value:
                # Make a comment informing the admins for this situation.
                # We are not going to fail this directly, as some criteria
                # answers can actually change over time. (For example: has
                # lived in Utrecht in the past month).
                comment = Comment()
                comment.comment = "Gave a different answer to a criteria " \
                                  "he/she answered before: {}, old answer: " \
                                  "{}, new answer: {}".format(
                    specific_criterion.criterion.name_natural,
                    answer.answer,
                    value
                )
                comment.participant = participant
                comment.experiment = experiment

                # NOTE: technically this is an illegal action as the
                # participant could not exist (yet). However, as the answer
                # object only exists if the participant exists, we're fine.
                comment.save()

                answer.answer = value
                answer.save()

    return failed_criteria, messages


def _handle_excluded_experiments(
        experiment: Experiment,
        participant: Participant
) -> Tuple[List[Experiment], List[str]]:
    invalid_experiments = []
    appointments = participant.appointments.all()
    participated_experiments = [x.timeslot.experiment for x in appointments]

    for excluded_experiment in experiment.excluded_experiments.all():
        if excluded_experiment in participated_experiments:
            invalid_experiments.append(excluded_experiment)

    messages = []
    if invalid_experiments:
        messages = [INVALID_EXPERIMENT_MESSAGE]

    return invalid_experiments, messages


def _handle_misc_items(data: dict, time_slot: TimeSlot) -> Tuple[list, list]:
    invalid_fields = []
    messages = []

    # Check if the timeslot is still free
    if not time_slot or not time_slot.has_free_places():
        invalid_fields.append('timeslot')
        messages.append(MISC_INVALID_MESSAGES['timeslot'])

    # Ensure this is a valid email address
    try:
        validate_email(data.get('email'))
        # Mini rant: Django, why isn't this call returning a boolean?
        # Why do I have to catch a Validation error? I get that it might be
        # easier in the whole validation framework, but then just use a helper
        # method that does `if not validate_email(email): raise ValidationError`
        # That would make this a lot nicer!
        # [/rant]
    except ValidationError:
        invalid_fields.append('email')
        messages.append(MISC_INVALID_MESSAGES['email'])

    return invalid_fields, messages


def _make_appointment(participant: Participant, time_slot: TimeSlot):
    appointment = Appointment()
    appointment.participant = participant
    appointment.timeslot = time_slot
    appointment.save()

    # TODO: sent mail


def _format_messages(*messages: List[str]) -> list:
    # Flatten the list of lists
    messages = [item for sublist in messages for item in sublist]

    admin = get_supreme_admin()
    contact_string = '<a href="mailto:{}">{}</a>'.format(
        admin.email,
        admin.get_full_name()
    )

    return [message.format(contact_string) for message in messages]
