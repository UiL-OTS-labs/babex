from typing import Tuple

from django.conf import settings

from api.auth.models import ApiUser
from main.utils import send_template_email
from participants.models import Participant


def send_password_reset_mail(user: ApiUser, token: str) -> None:
    link, alternative_link = _get_reset_links(token)

    subject = 'UiL OTS Experimenten: password reset'
    context = {
        'token':            token,
        'name':             _get_name(user),
        'link':             link,
        'alternative_link': alternative_link,
    }

    send_template_email(
        [user.email],
        subject,
        'api/mail/password_reset',
        context,
        'no-reply@uu.nl'
    )


def send_cancel_token_mail(participant: Participant, token: str,
                           email: str) -> None:
    link = "{}participant/appointments/{}/".format(settings.FRONTEND_URI, token)

    subject = 'UiL OTS Experimenten: afspraak afzeggen'
    context = {
        'token': token,
        'name':  participant.name or 'proefpersoon',
        'link':  link,
    }

    send_template_email(
        [email],
        subject,
        'api/mail/cancel_token',
        context,
        'no-reply@uu.nl'
    )


def _get_name(user: ApiUser) -> str:
    if hasattr(user, 'participant'):
        return user.participant.mail_name

    if hasattr(user, 'leader'):
        return user.leader.name

    return 'proefpersoon'


def get_reset_links(token: str) -> Tuple[str, str]:
    root = settings.FRONTEND_URI

    root = "{}reset_password/".format(root)

    complete = "{}{}/".format(root, token)

    return complete, root
