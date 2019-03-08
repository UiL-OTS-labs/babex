from rest_framework import views, viewsets, mixins as rest_mixins, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.auth.authenticators import JwtAuthentication
from api.auth.models import UserToken, ApiUser
from api.permissions import IsPermittedClient
from api.serializers import AppointmentSerializer
from api.utils import send_cancel_token_mail, cancel_appointment, \
    get_required_fields
from experiments.models import Appointment, Experiment
from participants.models import Participant


class SubscribeToEmaillistView(views.APIView):
    permission_classes = (IsPermittedClient,)

    def post(self, request):
        post_data = request.POST
        success = False

        email = post_data.get('email')

        qs = Participant.objects.prefetch_related('secondaryemail_set').all()

        filtered = [x for x in qs if x.email == email
                    or email
                    in [y.email for y in x.secondaryemail_set.all()]]

        alreadyKnown = len(filtered) != 0

        if not alreadyKnown:
            participant = Participant()

            participant.email = email
            participant.language = post_data.get('language')
            participant.multilingual = post_data.get('multilingual')
            participant.dyslexic = post_data.get('dyslexic')

            participant.save()
            success = True

        return Response({
            'success': success
        })


class GetAppointmentTokenView(views.APIView):
    permission_classes = (IsPermittedClient, )

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
    authentication_classes = (JwtAuthentication, )

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
                       rest_mixins.RetrieveModelMixin,
                       viewsets.GenericViewSet):
    permission_classes = (IsPermittedClient, )
    authentication_classes = (JwtAuthentication, )
    serializer_class = AppointmentSerializer

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

    def destroy(self, request, *args, **kwargs):
        # We do not need to do any checks, the _get_participant method call
        # in get_queryset() already does all required authentication checks.
        appointment = self.get_object()

        cancel_appointment(appointment)

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
