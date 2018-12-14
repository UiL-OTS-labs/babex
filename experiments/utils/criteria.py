from django.core.exceptions import ValidationError
from django.http import QueryDict
from uil.core.utils import set_model_field_value

from ..models import Criterium, ExperimentCriterium


def create_and_attach_criterium(experiment, name_form, name_natural, values,
                                correct_value, message_failed) -> None:
    """
    This function creates a new criterium, and uses :func:attach_criterium to
    attach it to an existing experiment.
    """
    criterium = Criterium()
    criterium.name_form = name_form
    criterium.name_natural = name_natural
    criterium.values = values
    criterium.save()

    attach_criterium(
        experiment,
        criterium,
        correct_value,
        message_failed,
    )


def attach_criterium(experiment, criterium, correct_value, message_failed):
    """
    This function attaches an existing criterium to an experiment, setting the
    proper values for such a link based upon the method parameters.
    """
    experiment_criterium = ExperimentCriterium()

    # We use this utility function so we can accept both pk values and model
    # instances
    set_model_field_value(experiment_criterium, 'criterium', criterium)
    set_model_field_value(experiment_criterium, 'experiment', experiment)

    experiment_criterium.correct_value = correct_value
    experiment_criterium.message_failed = message_failed
    experiment_criterium.save()


def clean_form_existing_criterium(post_data: QueryDict) -> dict:
    """Cleans the form data from the manual specific criteria form."""
    cleaned_data = {}
    # Get a proper dict, as the QueryDict is ****
    post_data = post_data.dict()

    criterium = post_data.get('criterium')
    cleaned_data['criterium'] = int(criterium)

    # Split the criterium_pk and the value, and check if the criterium_pk
    # matches the selected criterium value sent in POST
    check_pk, correct_value = post_data.get('correct_value').split('-', 2)

    if check_pk != criterium:
        raise ValidationError

    cleaned_data['correct_value'] = correct_value.strip()

    cleaned_data['message_failed'] = post_data.get('message_failed').strip()

    return cleaned_data
