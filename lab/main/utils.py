import urllib.parse as parse
from functools import lru_cache
from typing import List, Tuple

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection, send_mail
from django.template.loader import render_to_string
from django.utils import translation

from experiments.models import Experiment
from .models import User


@lru_cache(maxsize=None)
def get_supreme_admin() -> User:
    """
    The name is kinda a joke. It just returns the first User model that has
    the supreme_admin flag.

    The supreme admin is the one that's displayed on the site as the contact.
    :return:
    """
    return User.objects.filter(is_supreme_admin=True)[0]


def is_ldap_enabled() -> bool:
    return hasattr(settings, 'AUTH_LDAP_SERVER_URI')


def get_register_link(experiment: Experiment) -> str:
    return parse.urljoin(
        settings.FRONTEND_URI,
        "participant/register/{}/".format(
            experiment.pk,
        )
    )
