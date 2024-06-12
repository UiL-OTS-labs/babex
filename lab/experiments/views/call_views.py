import datetime

import ageutil
from cdh.core.mail import TemplateEmail
from django.conf import settings
from django.core.exceptions import BadRequest, PermissionDenied
from django.http.response import JsonResponse
from django.utils import timezone, translation
from django.utils.dateparse import parse_datetime
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from rest_framework import generics, serializers, views

from experiments.models import Appointment, Experiment, make_appointment
from experiments.models.invite_models import Call
from experiments.serializers import AppointmentSerializer, ExperimentSerializer
from mailauth.models import create_mail_auth
from main.auth.util import ExperimentLeaderMixin, IsExperimentLeader
from main.models import User
from main.serializers import UserSerializer
from participants.models import Participant
from participants.serializers import ParticipantSerializer
from utils.appointment_mail import prepare_appointment_mail, send_appointment_mail


class CallHomeView(ExperimentLeaderMixin, TemplateView):
    template_name = "call/home.html"

    @property
    def experiment(self):
        return Experiment.objects.get(pk=self.kwargs["experiment"])

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        experiment = Experiment.objects.get(pk=kwargs["experiment"])

        context["experiment"] = experiment
        context["experiment_serialized"] = ExperimentSerializer(experiment).data
        context["leaders"] = [UserSerializer(leader).data for leader in experiment.leaders.all()]

        participant = Participant.objects.get(pk=kwargs["participant"])
        context["participant"] = participant
        context["participant_serialized"] = ParticipantSerializer(participant).data

        # expose possible call statuses (except 'started' and 'confirmed' which we apply automatically)
        context["statuses"] = {
            id: str(title)
            for id, title in Call.CallStatus.choices
            if id not in [Call.CallStatus.STARTED, Call.CallStatus.CONFIRMED]
        }

        context["previous_calls"] = (
            Call.objects.filter(experiment=experiment, participant=participant)
            .exclude(status=Call.CallStatus.STARTED)
            .all()
        )

        call, created = Call.objects.get_or_create(
            experiment=experiment, participant=participant, leader=self.request.user, status=Call.CallStatus.STARTED
        )
        context["call"] = CallSerializer(call).data

        if not created:
            context["call_open"] = call

        dc = experiment.defaultcriteria
        age_pred = ageutil.age(months=dc.min_age_months, days=dc.min_age_days).to(
            months=dc.max_age_months, days=dc.max_age_days
        )

        context["participation_range"] = ageutil.date_of_birth(participant.birth_date).range_for(age_pred)

        return context


class AppointmentConfirm(generics.CreateAPIView):
    permission_classes = [IsExperimentLeader]
    serializer_class = AppointmentSerializer

    @property
    def experiment(self):
        return Experiment.objects.get(pk=self.request.data["experiment"])

    def create(self, request, *args, **kwargs):
        experiment = Experiment.objects.get(pk=request.data["experiment"])
        if not experiment.is_leader(request.user):
            raise PermissionDenied

        start = parse_datetime(request.data["start"])
        end = parse_datetime(request.data["end"])

        if end < start or start < timezone.now():
            raise BadRequest("Invalid appointment time")

        participant = Participant.objects.get(pk=request.data["participant"])

        if not self.check_age_at_appointment(participant, experiment, start):
            raise BadRequest("Invalid appointment time")

        leader = User.objects.filter(
            # make sure leader belongs to experiment
            experiments=experiment.pk
        ).get(
            pk=request.data["leader"],
        )

        appointment = make_appointment(experiment, participant, leader, start, end)
        return JsonResponse(self.serializer_class(appointment).data)

    def check_age_at_appointment(self, participant: Participant, experiment: Experiment, start: datetime.date) -> bool:
        criteria = experiment.defaultcriteria
        age_pred = (
            ageutil.age(months=criteria.min_age_months, days=criteria.min_age_days)
            .to(months=criteria.max_age_months, days=criteria.max_age_days)
            .on(start)
        )
        return age_pred.check(participant.birth_date)


class AppointmentSendEmail(views.APIView):
    permission_classes = [IsExperimentLeader]

    @property
    def experiment(self):
        pk = self.request.data.get("id", self.kwargs.get("pk"))
        return Appointment.objects.get(pk=pk).experiment

    def get(self, request, *args, **kwargs):
        """Returns the email template that's relevant for a given appointment.
        Used to populate client-side editor"""
        appointment = Appointment.objects.get(pk=int(kwargs["pk"]))
        return JsonResponse(dict(content=prepare_appointment_mail(appointment)))

    def post(self, request, *args, **kwargs):
        """Sends a custom email"""
        appointment = Appointment.objects.get(pk=int(request.data["id"]))
        if not appointment.experiment.is_leader(request.user):
            raise PermissionDenied
        content = request.data["content"]
        send_appointment_mail(appointment, content)
        return JsonResponse({})


class CallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Call
        fields = ["id", "status", "experiment", "participant", "leader", "creation_date", "comment"]


class UpdateCall(generics.UpdateAPIView):
    permission_classes = [IsExperimentLeader]
    serializer_class = CallSerializer

    @property
    def experiment(self):
        return Call.objects.get(pk=self.kwargs["pk"]).experiment

    def update(self, request, *args, **kwargs):
        call = Call.objects.get(pk=kwargs["pk"])
        if call.leader != request.user:
            raise PermissionDenied

        call.status = request.data["status"]
        call.comment = request.data["comment"]
        call.save()

        if call.status == Call.CallStatus.DEACTIVATE:
            # this happens when an experiment leader talks to a parent on the phone and they ask
            # to be removed from the database.
            # we decided that we don't want to apply this directly, but rather send the parent a link
            # to the page where they can deregister themselves.
            expiry = timezone.now() + datetime.timedelta(days=7)
            mauth = create_mail_auth(expiry, participant=call.participant)
            deactivate_link = mauth.get_link("/data/")

            with translation.override("nl"):
                mail = TemplateEmail(
                    html_template="mail/deactivate.html",
                    context=dict(
                        base_url=settings.PARENT_URI, name=call.participant.parent_name, deactivate_link=deactivate_link
                    ),
                    to=[call.participant.email],
                    subject=_("experiments:call:deactivate:mail:subject"),
                )
            mail.send()
        return JsonResponse(self.serializer_class(call).data)
