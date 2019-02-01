from django.conf import settings

from api.auth.models import ApiUser
from main.utils import send_template_email


def send_password_reset_mail(user: ApiUser, token: str) -> None:
    link, alternative_link = get_reset_links(token)

    subject = 'UiL OTS Experimenten: password reset'
    context = {
        'token': token,
        'name': _get_name(user),
        'link': link,
        'alternative_link': alternative_link,
    }

    send_template_email(
        [user.email],
        subject,
        'api/mail/password_reset',
        context,
        'no-reply@uu.nl'
    )


def _get_name(user: ApiUser):

    if hasattr(user, 'participant'):
        return user.participant.mail_name

    if hasattr(user, 'leader'):
        return user.leader.name

    return 'proefpersoon'


def get_reset_links(token: str):
    root = settings.FRONTEND_URI

    root = "{}reset_password/".format(root)

    complete = "{}{}/".format(root, token)

    return complete, root
