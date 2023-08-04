from datetime import datetime, timedelta

from rest_framework import exceptions, views
from rest_framework.response import Response

from participants.models import Participant
from participants.serializers import ParticipantSerializer

from .models import create_mail_auth, resolve_participant, try_authenticate


class MailAuthView(views.APIView):
    def get(self, request, *args, **kwargs):
        if "token" not in kwargs:
            return Response(dict())

        # look for valid auth object for token
        mauth, possible_pps = try_authenticate(kwargs["token"])
        if mauth is not None:
            # valid token
            return Response(
                dict(
                    session_token=mauth.session_token,
                    possible_pps=[ParticipantSerializer(pp).data for pp in possible_pps],
                )
            )
        raise exceptions.AuthenticationFailed()

    def post(self, request, *args, **kwargs):
        email = request.data["email"]

        participant = Participant.objects.efilter(deactivated=None, email=email)
        try:
            # read from generator
            next(participant)
        except StopIteration:
            # TODO: perhaps better to display a message that says
            # "if the address exists in our system you will shortly receive an email"
            # instead of revealing whether an email address appears in our db or not
            raise exceptions.AuthenticationFailed()

        # email exists, generate token and send it
        expiry = datetime.now() + timedelta(hours=24)
        mauth = create_mail_auth(expiry, email)
        mauth.send()
        return Response(dict())


class SetParticipantView(views.APIView):
    def post(self, request, *args, **kwargs):
        try:
            token = request.headers.get("Authorization").split(" ")[1]
        except Exception:
            raise exceptions.PermissionDenied()

        if resolve_participant(token, request.data["participant_id"]):
            return Response(dict())
        raise exceptions.PermissionDenied()
