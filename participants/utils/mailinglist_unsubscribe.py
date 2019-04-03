from django.conf import settings

from api.auth.models import UserToken
from participants.models import Participant


def get_mailinglist_unsubscribe_token(participant: Participant) -> UserToken:
    try:
        token = UserToken.objects.get(
            participant=participant,
            type=UserToken.MAILINGLIST_UNSUBSCRIBE
        )

    except UserToken.DoesNotExist:
        token = UserToken(
            participant=participant,
            type=UserToken.MAILINGLIST_UNSUBSCRIBE,
        )
        token.save()

    return token


def get_mailinglist_unsubscribe_url(participant: Participant):
    token = get_mailinglist_unsubscribe_token(participant)

    return "{}participant/unsubscribe_mailinglist/{}/".format(
        settings.FRONTEND_URI,
        token.token
    )
