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

        pps = Participant.find_by_email(email)
        if len(pps) < 1:
            # fail silently to avoid revealing whether an email address appears in our db
            return Response(dict())

        # email exists, generate token and send it
        expiry = datetime.now() + timedelta(hours=24)
        mauth = create_mail_auth(expiry, email)

        # while there might be multiple participants matching the given email address,
        # we assume they all use the same parent name.
        parent_name = pps[-1].parent_name
        mauth.send(parent_name)
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
