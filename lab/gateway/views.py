from django.utils import timezone
from rest_framework import generics, mixins, permissions, views, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from experiments.serializers import ParentAppointmentSerializer
from participants.models import Language
from participants.serializers import LanguageSerializer
from signups.models import Signup
from signups.serializers import SignupSerializer
from survey_admin.models import SurveyDefinition, SurveyResponse
from survey_admin.serializers import (
    SurveyDefinitionSerializer,
    SurveyInviteSerializer,
    SurveyResponseSerializer,
)


class HasParticipant(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.participant is not None


class SignedSource(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.signed is True


class GatewayHome(views.APIView):
    permission_classes = [SignedSource]

    def get(self, request, *args, **kwargs):
        return Response(dict())


class Signups(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = Signup.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [SignedSource]

    def perform_create(self, serializer):
        super().perform_create(serializer)
        serializer.instance.send_email_validation()


class SessionView(views.APIView):
    permission_classes = [HasParticipant, SignedSource]

    def get(self, request, *args, **kwargs):
        return Response(dict(name=self.request.participant.name))


class AppointmentViewSet(viewsets.ModelViewSet):
    permission_classes = [HasParticipant, SignedSource]
    serializer_class = ParentAppointmentSerializer

    def get_queryset(self):
        return self.request.participant.appointments.all()

    def perform_destroy(self, appointment):
        # using DELETE to cancel appointment
        appointment.cancel()


class SurveyView(generics.RetrieveAPIView):
    permission_classes = [HasParticipant, SignedSource]
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
    permission_classes = [HasParticipant, SignedSource]
    serializer_class = SurveyInviteSerializer

    def get_queryset(self):
        return self.request.participant.survey_invites.all()


class SurveyViewSet(viewsets.ModelViewSet):
    permission_classes = [HasParticipant, SignedSource]
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


class DeactivateView(views.APIView):
    permission_classes = [HasParticipant, SignedSource]

    def post(self, request, *args, **kwargs):
        self.request.participant.deactivate()
        return Response(dict())


class LanguagesView(generics.ListAPIView):
    permission_classes = [SignedSource]

    serializer_class = LanguageSerializer
    queryset = Language.objects.all()
