from rest_framework import generics, mixins, permissions, views, viewsets
from rest_framework.response import Response

from experiments.serializers import AppointmentSerializer
from signups.models import Signup
from signups.serializers import SignupSerializer
from survey_admin.models import SurveyDefinition
from survey_admin.serializers import SurveyDefinitionSerializer, SurveyInviteSerializer


class GatewayHome(views.APIView):
    def get(self, request, *args, **kwargs):
        return Response(dict())


class Signups(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = Signup.objects.all()
    serializer_class = SignupSerializer


class HasParticipant(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.participant is not None


class AppointmentsView(generics.ListAPIView):
    # TODO: this is just an example of providing participant data to the parent app
    permission_classes = [HasParticipant]
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        return self.request.participant.appointments.all()


class SurveyView(generics.RetrieveAPIView):
    permission_classes = [HasParticipant]
    serializer_class = SurveyDefinitionSerializer
    queryset = SurveyDefinition.objects.all()

    def get_queryset(self):
        # queryset should only contain surveys the participant was invited to fill
        return SurveyDefinition.objects.filter(surveyinvite__participant=self.request.participant)


class SurveyInvitesView(generics.ListAPIView):
    permission_classes = [HasParticipant]
    serializer_class = SurveyInviteSerializer

    def get_queryset(self):
        return self.request.participant.survey_invites.all()
