import dateutil.parser
from django.core.exceptions import BadRequest
from django.utils import timezone
from django.views import generic
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response

from experiments.models import Appointment, Experiment, Location
from experiments.serializers import AppointmentSerializer
from main.auth.util import (
    IsExperimentLeader,
    LabManagerMixin,
    LabSupportMixin,
    RandomLeaderMixin,
)
from utils.appointment_mail import prepare_appointment_mail, send_appointment_mail

from .models import Closing, ClosingSerializer


class AppointmentFeed(RandomLeaderMixin, generics.ListAPIView):
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        from_date = dateutil.parser.parse(self.request.GET["start"])
        to_date = dateutil.parser.parse(self.request.GET["end"])

        # the experiment parameter is used to retrieve a feed that's relevant for a given experiment
        # practically, that means appointments of any experiement taking place at the relevant location
        experiment_id = self.request.GET.get("experiment")
        appointments = Appointment.objects.filter(timeslot__start__gte=from_date, timeslot__end__lt=to_date)
        if experiment_id:
            experiment = Experiment.objects.get(pk=experiment_id)
            appointments = appointments.filter(experiment__location=experiment.location)
        return appointments


class AgendaHome(RandomLeaderMixin, generic.TemplateView):
    template_name = "agenda/home.html"

    def _format_location(self, location: Location):
        return dict(id=location.id, name=location.name)

    def get_context_data(self, *args, **kwargs):
        locations = Location.objects.all()

        return dict(locations=[self._format_location(x) for x in locations], date=self.kwargs.get("date"))


class ClosingPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == "list":
            return True
        return request.user.is_support or request.user.is_staff


class ClosingViewSet(viewsets.ModelViewSet):
    serializer_class = ClosingSerializer
    permission_classes = [ClosingPermission]

    def get_queryset(self):
        queryset = Closing.objects.all()
        if self.request.method == "GET":
            from_date = dateutil.parser.parse(self.request.GET["start"])
            to_date = dateutil.parser.parse(self.request.GET["end"])

            # the experiment parameter is used to retrieve a feed that's relevant for a given experiment
            # practically, that means closings of the relevant location, or the entire building
            experiment_id = self.request.GET.get("experiment")
            queryset = queryset.filter(end__gte=from_date, start__lt=to_date)
            if experiment_id:
                experiment = Experiment.objects.get(pk=experiment_id)
                if experiment.location.part_of_building:
                    queryset = queryset.filter(location=experiment.location).union(queryset.filter(is_global=True))
                else:
                    queryset = queryset.filter(location=experiment.location)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsExperimentLeader]

    @property
    def experiment(self):
        return self.get_object().experiment

    def get_queryset(self):
        queryset = Appointment.objects.all()
        return queryset

    def perform_destroy(self, appointment: Appointment):
        appointment.cancel()

    def perform_update(self, serializer):
        original_start = self.get_object().timeslot.start
        updated_start = serializer.validated_data["start"]
        # check that new time is valid
        if original_start != updated_start and updated_start < timezone.now():
            raise BadRequest("Invalid appointment time")

        updated = serializer.save()

        # check if we should inform the participant about changed time
        if original_start != updated_start:
            # we potentially have to send a new reminder mail later
            updated.reminder_sent = None
            updated.save()

            if not self.request.data.get("silent"):
                send_appointment_mail(updated, prepare_appointment_mail(updated))


class ClosingsAdminView(LabSupportMixin, generic.TemplateView):
    template_name = "agenda/closings_admin.html"

    def get_context_data(self, **kwargs):
        context = dict()
        context["object_list"] = self.get_object_list()
        return context

    def get_object_list(self):
        return Closing.objects.all().order_by("-start")

    def post(self, request, *args, **kwargs):
        """simple post endpoint for removing closings"""
        pks = map(int, request.POST.getlist("closings"))
        Closing.objects.filter(pk__in=pks).delete()
        return self.get(request, *args, **kwargs)
