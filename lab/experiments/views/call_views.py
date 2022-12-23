from datetime import datetime
import braces.views as braces
from django.core.exceptions import BadRequest
from django.views.generic import TemplateView
from django.http.response import JsonResponse
from django.utils.dateparse import parse_datetime

import ageutil
from rest_framework import generics, serializers, views
from rest_framework.permissions import IsAdminUser


from utils.appointment_mail import send_appointment_mail
from experiments.models import Experiment, Appointment, TimeSlot
from experiments.models.invite_models import Call
from experiments.serializers import AppointmentSerializer, ExperimentSerializer
from leaders.models import Leader
from leaders.serializers import LeaderSerializer
from participants.models import Participant
from participants.serializers import ParticipantSerializer


class CallHomeView(braces.LoginRequiredMixin, TemplateView):
    template_name = 'call/home.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        experiment = Experiment.objects.get(pk=kwargs['experiment'])

        context['experiment'] = experiment
        context['experiment_serialized'] = ExperimentSerializer(experiment).data
        context['leaders'] = [LeaderSerializer(leader).data for leader in experiment.leaders.all()]

        participant = Participant.objects.get(pk=kwargs['participant'])
        context['participant'] = participant
        context['participant_serialized'] = ParticipantSerializer(participant).data

        # expose possible call statuses (except 'started' and 'confirmed' which we apply automatically)
        context['statuses'] = {id: str(title) for id, title in Call.CallStatus.choices
                               if id not in [Call.CallStatus.STARTED, Call.CallStatus.CONFIRMED]}

        context['previous_calls'] = Call.objects.filter(experiment=experiment,
                                                        participant=participant)\
                                                .exclude(status=Call.CallStatus.STARTED).all()

        call, created = Call.objects.get_or_create(
            experiment=experiment,
            participant=participant,
            leader=self.request.user.leader,
            status=Call.CallStatus.STARTED
        )
        context['call'] = CallSerializer(call).data

        if not created:
            context['call_open'] = call

        dc = experiment.defaultcriteria
        age_pred = ageutil.age(months=dc.min_age_months, days=dc.min_age_days)\
                          .to(months=dc.max_age_months, days=dc.max_age_days)

        context['participation_range'] = ageutil.date_of_birth(participant.birth_date).range_for(age_pred)

        return context


class AppointmentConfirm(generics.CreateAPIView):
    permission_classes = [IsAdminUser]  # TODO: check if user is a leader of the experiment
    serializer_class = AppointmentSerializer

    def create(self, request, *args, **kwargs):
        experiment = Experiment.objects.get(pk=request.data['experiment'])
        start = parse_datetime(request.data['start'])
        end = parse_datetime(request.data['end'])

        if end < start or start < datetime.now():
            raise BadRequest('Invalid appointment time')

        timeslot = TimeSlot.objects.create(
            start=start,
            end=end,
            experiment=experiment,
            max_places=1
        )

        leader = Leader.objects.filter(
            # make sure leader belongs to experiment
            experiments=experiment.pk
        ).get(
            pk=request.data['leader'],
        )

        participant = Participant.objects.get(pk=request.data['participant'])
        appointment = Appointment.objects.create(
            participant=participant, timeslot=timeslot, experiment=experiment, leader=leader)

        if request.data['emailParticipant']:
            send_appointment_mail(appointment)

        return JsonResponse(self.serializer_class(appointment).data)


class AppointmentSendEmail(views.APIView):
    permission_classes = [IsAdminUser]  # TODO: check if user is a leader of the experiment

    def get(self, request, *args, **kwargs):
        """Returns the email template that's relevant for a given appointment.
        Used to populate client-side editor"""
        appointment = Appointment.objects.get(pk=int(kwargs['pk']))
        return JsonResponse(dict(content=appointment.experiment.confirmation_email))

    def post(self, request, *args, **kwargs):
        """Sends a custom email"""
        appointment = Appointment.objects.get(pk=int(request.data['id']))
        content = request.data['content']
        send_appointment_mail(appointment, content)
        return JsonResponse({})


class CallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Call
        fields = ['id', 'status', 'experiment', 'participant', 'leader', 'creation_date', 'comment']


class UpdateCall(generics.UpdateAPIView):
    permission_classes = [IsAdminUser]  # TODO: check if user started the call
    serializer_class = CallSerializer

    def update(self, request, *args, **kwargs):
        call = Call.objects.get(pk=kwargs['pk'])
        call.status = request.data['status']
        call.comment = request.data['comment']
        call.save()

        return JsonResponse(self.serializer_class(call).data)
