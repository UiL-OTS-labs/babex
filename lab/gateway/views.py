from rest_framework import generics, mixins, permissions, views, viewsets
from rest_framework.response import Response

from experiments.serializers import AppointmentSerializer
from signups.models import Signup
from signups.serializers import SignupSerializer
from survey_admin.models import SurveyDefinition, SurveyResponse
from survey_admin.serializers import (
    SurveyDefinitionSerializer,
    SurveyInviteSerializer,
    SurveyResponseSerializer,
)


class GatewayHome(views.APIView):
    def get(self, request, *args, **kwargs):
        return Response(dict())


class Signups(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = Signup.objects.all()
    serializer_class = SignupSerializer

    def perform_create(self, serializer):
        super().perform_create(serializer)
        serializer.instance.send_email_validation()


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

    def get_object(self):
        # resolve Survey model via invite
        invite = self.request.participant.survey_invites.get(pk=self.kwargs["invite_id"])
        return invite.survey


class SurveyInvitesView(generics.ListAPIView):
    permission_classes = [HasParticipant]
    serializer_class = SurveyInviteSerializer

    def get_queryset(self):
        return self.request.participant.survey_invites.all()


class SurveyResponseView(generics.CreateAPIView):
    permission_classes = [HasParticipant]
    serializer_class = SurveyResponseSerializer

    def create(self, request, *args, **kwargs):
        invite = self.request.participant.survey_invites.get(pk=self.request.data["invite_id"])
        SurveyResponse.objects.create(invite=invite, data=self.request.data["data"])
        return Response({})
