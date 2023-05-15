from django.utils import timezone
from rest_framework import generics, mixins, permissions, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from experiments.serializers import AppointmentSerializer
from signups.models import Signup
from signups.serializers import SignupSerializer
from survey_admin.models import SurveyDefinition, SurveyInvite, SurveyResponse
from survey_admin.serializers import (
    SurveyDefinitionSerializer,
    SurveyInviteSerializer,
    SurveyResponseSerializer,
)
from utils.cancel_appointment import cancel_appointment


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


class AppointmentViewSet(viewsets.ModelViewSet):
    permission_classes = [HasParticipant]
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        return self.request.participant.appointments.all()

    def perform_destroy(self, appointment):
        # using DELETE to cancel appointment
        cancel_appointment(appointment)


class SurveyView(generics.RetrieveAPIView):
    permission_classes = [HasParticipant]
    serializer_class = SurveyDefinitionSerializer
    queryset = SurveyDefinition.objects.all()

    def get_object(self):
        # resolve Survey model via invite
        invite = self.request.participant.survey_invites.get(pk=self.kwargs["invite_id"])
        if hasattr(invite, "surveyresponse"):
            # survey response was already sent
            raise APIException("Survey already completed")
        return invite.survey


class SurveyInvitesView(generics.ListAPIView):
    permission_classes = [HasParticipant]
    serializer_class = SurveyInviteSerializer

    def get_queryset(self):
        return self.request.participant.survey_invites.all()


class SurveyViewSet(viewsets.ModelViewSet):
    permission_classes = [HasParticipant]
    serializer_class = SurveyDefinitionSerializer
    lookup_field = "surveyinvite"
    lookup_url_kwarg = "pk"

    def get_queryset(self):
        return SurveyDefinition.objects.filter(surveyinvite__participant=self.request.participant)

    @action(detail=True)
    def response(self, request, pk):
        invite = self.request.participant.survey_invites.get(pk=pk)
        if hasattr(invite, "surveyresponse"):
            return Response(SurveyResponseSerializer(invite.surveyresponse).data)
        return Response(dict())

    @response.mapping.post
    def submit_response(self, request, pk):
        return self.save_response(pk, is_completed=self.request.data.get("final", False))

    def save_response(self, pk, is_completed):
        completed = timezone.now() if is_completed else None
        response, _ = SurveyResponse.objects.update_or_create(
            invite_id=pk,
            defaults=dict(
                data=self.request.data["data"],
                page=self.request.data.get("page", 0),
                completed=completed,
            ),
        )
        serializer = SurveyResponseSerializer(response)
        return Response(serializer.data)
