from datetime import datetime, timedelta
from secrets import token_urlsafe
from typing import List, Optional, Tuple

import cdh.core.fields as e_fields
from cdh.mail.classes import TemplateEmail
from django.conf import settings
from django.db import models

from participants.models import Participant


class MailAuth(models.Model):
    email = e_fields.EncryptedEmailField()
    created = models.DateTimeField(auto_now_add=True)
    expiry = models.DateTimeField()
    # used in mail sent to parent for authentication
    link_token = models.CharField(max_length=64, default=token_urlsafe, unique=True)
    # null by default, generated upon succesful login. Has to be present in any (non-login) request.
    session_token = models.CharField(max_length=64, null=True, unique=True)

    participant = models.ForeignKey("participants.Participant", on_delete=models.CASCADE, null=True)

    def send(self):
        mail = TemplateEmail(
            html_template="mailauth/link.html",
            context=dict(
                base_url=settings.PARENT_URI,
                link_token=self.link_token,
            ),
            to=[self.email],
            subject="login link",
        )
        mail.send()

    def get_link(self, redirect=None):
        return settings.PARENT_URI + f"auth/{self.link_token}?redirect={redirect}"


def create_mail_auth(
    expiry: datetime, email: Optional[str] = None, participant: Optional[Participant] = None
) -> MailAuth:
    """There are two general scenarios where we would like to create a mail authentication token:
    1. The parent enters their email on the login page.
       In this case we send a token that identifies them by email, and later have to
       potentially disambiguate between multiple participants, in case they have more than one child.
    2. The parents are mailed by the system in the context of a specific experiment.
       In this case we should already precisely know who is the relevant participant, and can
       save them in the MailAuth object
    """
    if not email and not participant:
        raise ValueError("Either email or participant must be specified")

    if participant and not email:
        email = participant.email

    assert email
    # participant could still be None, to indicate it must be later resolved
    return MailAuth.objects.create(expiry=expiry, email=email, participant=participant)


def try_authenticate(token: str) -> Tuple[Optional[MailAuth], List[Participant]]:
    try:
        mauth = MailAuth.objects.get(
            link_token=token,
            # link should not be too old
            expiry__gte=datetime.now(),
        )
    except MailAuth.DoesNotExist:
        return None, []

    possible_pps = []
    if not mauth.participant:
        # specific participant wasn't already chosen

        participants = Participant.find_by_email(mauth.email)
        if len(participants) == 1:
            # only one participant associated with email, assign it immediately
            mauth.participant = participants[0]
        else:
            # reaching here means that there are multiple participants associated with
            # the user's email, and a single participant was not yet chosen.
            # it is expected that the user indicates the relevant participant and that
            # the parent app sets it via an api call
            possible_pps = participants

    mauth.session_token = token_urlsafe()
    mauth.save()
    return mauth, possible_pps


def lookup_session_token(token: str) -> Optional[Participant]:
    """Retrieves the relevant Participant for the current session, if one has been set"""
    if not token:
        # never accept an empty string as a token
        return None

    try:
        mauth = MailAuth.objects.get(
            session_token=token,
        )
    except MailAuth.DoesNotExist:
        return None

    return mauth.participant


def resolve_participant(token: str, participant_id: int) -> bool:
    """Sets the participant attribute for a MailAuth session identified
    by a session token"""
    try:
        mauth = MailAuth.objects.get(
            session_token=token,
        )
    except MailAuth.DoesNotExist:
        return False

    if mauth.participant is not None:
        # participant was already set for the session, don't allow overriding it
        return False

    try:
        pp = Participant.objects.get(pk=participant_id, deactivated=None)
    except Participant.DoesNotExist:
        return False

    # important to check the email, so that the participant id cannot
    # be freely set to whatever
    if pp.email != mauth.email:
        return False
    mauth.participant = pp

    mauth.save()
    return True
