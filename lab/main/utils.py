import urllib.parse as parse

from django.conf import settings

from experiments.models import Experiment


def get_register_link(experiment: Experiment) -> str:
    return parse.urljoin(
        settings.FRONTEND_URI,
        "participant/register/{}/".format(
            experiment.pk,
        ),
    )
