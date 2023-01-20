import urllib.parse as parse

from django.conf import settings

from experiments.models import Experiment


def is_ldap_enabled() -> bool:
    return hasattr(settings, 'AUTH_LDAP_SERVER_URI')


def get_register_link(experiment: Experiment) -> str:
    return parse.urljoin(
        settings.FRONTEND_URI,
        "participant/register/{}/".format(
            experiment.pk,
        )
    )
