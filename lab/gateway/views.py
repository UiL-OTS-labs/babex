from rest_framework import generics, mixins, permissions, views, viewsets
from rest_framework.response import Response

from experiments.serializers import AppointmentSerializer
from signups.models import Signup
from signups.serializers import SignupSerializer


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
