from django.core.exceptions import ValidationError
from django.db import DatabaseError
from rest_framework import views, viewsets, mixins as rest_mixins, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.auth.authenticators import JwtAuthentication
from api.auth.models import UserToken
from api.permissions import IsPermittedClient
from api.serializers import AppointmentSerializer
from api.utils import send_cancel_token_mail, cancel_appointment, \
    get_required_fields
from auditlog.enums import Event, UserType
import auditlog.utils.log as auditlog
from experiments.models import Appointment, Experiment
from participants.models import Participant


class SubscribeToEmaillistView(views.APIView):
    permission_classes = (IsPermittedClient,)

    def post(self, request):
        post_data = request.POST
        success = False

        email = post_data.get('email').strip()

        filtered = Participant.objects.find_by_email(email)

        already_known = len(filtered) != 0

        # Initialize it here
        participant = None

        if already_known:
            participant = filtered[0]
        else:
            participant = Participant()

            participant.email = email
            participant.language = post_data.get('language')
            participant.multilingual = post_data.get('multilingual')
            participant.dyslexic = post_data.get('dyslexic')
            participant.email_subscription = True

        try:
            participant.email_subscription = True
            participant.save()
            success = True
        except (DatabaseError, AttributeError):
            pass

        return Response({
            'success': success
        })


class ValidateMailinglistTokenView(views.APIView):
    permission_classes = (IsPermittedClient,)

    def post(self, request):

        token = request.POST.get('token', None)

        success = False
        email = None

        if token:
            try:
                o = UserToken.objects.get(
                    token=token,
                    type=UserToken.MAILINGLIST_UNSUBSCRIBE,
                )

                # Please note that these token's don't have to be checked for
                # expiration. These tokens should just live on indefinably

                success = True
                email = o.participant.email

            except (ValidationError, UserToken.DoesNotExist):
                pass

        return Response({
            'success': success,
            'email':   email
        })


class UnsubscribeFromMailinglistView(views.APIView):
    permission_classes = (IsPermittedClient,)

    def post(self, request):
        token = request.POST.get('token', None)

        success = False

        if token:
            try:
                o = UserToken.objects.get(
                    token=token,
                    type=UserToken.MAILINGLIST_UNSUBSCRIBE,
                )

                # Please note that these token's don't have to be checked for
                # expiration. These tokens should just live on indefinably.

                participant = o.participant
                participant.email_subscription = False
                participant.save()

                success = True

            except (ValidationError, UserToken.DoesNotExist):
                pass

        return Response({
            'success': success,
        })


class GetAppointmentTokenView(views.APIView):
    permission_classes = (IsPermittedClient,)

    def post(self, request):
        to_lower = lambda x: str(x).lower()

        email = request.POST.get('email', None)
        email = to_lower(email)

        success = False

        if email:
            participants = [x for x in
                            Participant.objects.prefetch_related(
                                'secondaryemail_set'
                            ) if
                            to_lower(x.email) == email or
                            email in [to_lower(y.email) for y in
                                      x.secondaryemail_set.all()]
                            ]

            if len(participants) == 1:
                participant = participants[0]

                token = UserToken.objects.create(
                    participant=participant,
                    type=UserToken.CANCEL_APPOINTMENTS,
                )

                # We send the given email along, as the user will be
                # expecting an email on that address. (Which may or may not
                # be the primary email).
                send_cancel_token_mail(
                    participant,
                    str(token.token),
                    email
                )

                success = True

        return Response({
            'success': success
        })


class GetRequiredFields(views.APIView):
    permission_classes = (IsPermittedClient, IsAuthenticated)
    authentication_classes = (JwtAuthentication,)

    def get(self, request, *args, **kwargs):
        fields = None

        if request.user.is_participant:
            participant = request.user.participant
            experiment = Experiment.objects.get(
                pk=kwargs.get('experiment')
            )

            fields = get_required_fields(experiment, participant)

        if not fields:
            fields.append('__all__')

        return Response({
            'fields': fields
        })


class AppointmentsView(rest_mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    permission_classes = (IsPermittedClient,)
    authentication_classes = (JwtAuthentication,)
    serializer_class = AppointmentSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        message = "Participant viewed appointment for experiment '{}'".format(
            instance.experiment.name
        )

        event = Event.VIEW_DATA

        auditlog.log(
            event,
            message,
            self.request.user,
            UserType.PARTICIPANT,
        )

        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        message = "Participant viewed entire list of their appointments"

        event = Event.VIEW_DATA

        auditlog.log(
            event,
            message,
            self.request.user,
            UserType.PARTICIPANT,
            {
                'pk_list': [x.pk for x in queryset]
            }
        )

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        # We do not need to do any checks, the _get_participant method call
        # in get_queryset() already does all required authentication checks.
        appointment = self.get_object()

        message = "Participant deleted appointment for experiment '{}'".format(
            appointment.experiment.name
        )

        event = Event.DELETE_DATA

        auditlog.log(
            event,
            message,
            self.request.user,
            UserType.PARTICIPANT,
        )

        cancel_appointment(appointment)

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )

    def _get_participant(self):
        if self.request.user.is_authenticated and \
                self.request.user.is_participant:
            return self.request.user.participant

        if 'user_token' in self.request.GET:
            token = UserToken.objects.get(
                type=UserToken.CANCEL_APPOINTMENTS,
                token=self.request.GET.get('user_token'),
            )

            if token.is_valid():
                return token.participant
            else:
                token.delete()

        # No authentication was found, so we cannot get a participant
        raise PermissionDenied

    def get_queryset(self):
        return Appointment.objects.filter(participant=self._get_participant())
