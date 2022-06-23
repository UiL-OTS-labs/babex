from django.core.exceptions import ValidationError
from django.http import QueryDict
from uil.core.utils import set_model_field_value

from ..models import Criterion, ExperimentCriterion


def create_and_attach_criterion(experiment, name_form, name_natural, values,
                                correct_value, message_failed) -> None:
    """
    This function creates a new criterion, and uses :func:attach_criterion to
    attach it to an existing experiment.
    """
    criterion = Criterion()
    criterion.name_form = name_form
    criterion.name_natural = name_natural
    criterion.values = values
    criterion.save()

    attach_criterion(
        experiment,
        criterion,
        correct_value,
        message_failed,
    )


def attach_criterion(experiment, criterion, correct_value, message_failed):
    """
    This function attaches an existing criterion to an experiment, setting the
    proper values for such a link based upon the method parameters.
    """
    experiment_criterion = ExperimentCriterion()

    # We use this utility function so we can accept both pk values and model
    # instances
    set_model_field_value(experiment_criterion, 'criterion', criterion)
    set_model_field_value(experiment_criterion, 'experiment', experiment)

    experiment_criterion.correct_value = correct_value
    experiment_criterion.message_failed = message_failed
    experiment_criterion.save()


def clean_form_existing_criterion(post_data: QueryDict) -> dict:
    """Cleans the form data from the manual specific criteria form."""
    cleaned_data = {}
    # Get a proper dict, as the QueryDict is ****
    post_data = post_data.dict()

    criterion = post_data.get('criterion')
    cleaned_data['criterion'] = int(criterion)

    # Split the criterion_pk and the value, and check if the criterion_pk
    # matches the selected criterion value sent in POST
    check_pk, correct_value = post_data.get('correct_value').split('-', 2)

    if check_pk != criterion:
        raise ValidationError

    cleaned_data['correct_value'] = correct_value.strip()

    cleaned_data['message_failed'] = post_data.get('message_failed').strip()

    return cleaned_data
