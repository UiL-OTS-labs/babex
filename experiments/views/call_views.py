import braces.views as braces
from django.views.generic import TemplateView
from django.http.response import JsonResponse

import ageutil
from rest_framework import generics, serializers
from rest_framework.permissions import IsAdminUser


from experiments.models import Experiment, Appointment, TimeSlot
from experiments.models.invite_models import Call
from api.serializers.experiment_serializers import ExperimentSerializer
from api.serializers.leader_serializers import LeaderSerializer
from api.serializers.participant_serializers import ParticipantSerializer
from participants.models import Participant


class CallHomeView(braces.LoginRequiredMixin, TemplateView):
    template_name = 'call/home.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        experiment = Experiment.objects.get(pk=kwargs['experiment'])

        context['experiment'] = experiment
        context['experiment_serialized'] = ExperimentSerializer(experiment).data
        context['leaders'] = [LeaderSerializer(leader).data for leader in experiment.leaders]

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

        min_age, max_age = experiment.defaultcriteria.min_age, experiment.defaultcriteria.max_age
        if min_age == -1 and max_age == -1:
            # no age limits, unlikely but still supported
            age_pred = None
        elif min_age != -1 and max_age == -1:
            age_pred = ageutil.age(months=min_age).or_older()
        elif min_age == -1 and max_age != -1:
            age_pred = ageutil.age(months=max_age).or_younger()
        else:
            age_pred = ageutil.age(months=min_age).to(months=max_age)

        if age_pred is not None:
            context['participation_range'] = ageutil.dob(participant.birth_date).range_for(age_pred)

        return context


class AppointmentConfirm(generics.CreateAPIView):
    permission_classes = [IsAdminUser]  # TODO: check if user is a leader of the experiment

    def create(self, request, *args, **kwargs):
        experiment = Experiment.objects.get(pk=request.data['experiment'])

        timeslot = TimeSlot.objects.create(
            start=request.data['start'],
            end=request.data['end'],
            experiment=experiment,
            max_places=1
        )

        Appointment.objects.create(
            participant=Participant.objects.get(pk=request.data['participant']),
            timeslot=timeslot,
            experiment=experiment,
        )

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