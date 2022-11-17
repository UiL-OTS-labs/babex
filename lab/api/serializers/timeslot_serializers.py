from rest_framework import serializers

from api.serializers.participant_serializers import ParticipantSerializer, \
    LeaderParticipantSerializer
from experiments.models import TimeSlot, Appointment


class LeaderTimeSlotSerializer(serializers.ModelSerializer):
    appointments = serializers.SerializerMethodField()

    class Meta:
        model = TimeSlot
        depth = 1
        fields = [
            'id', 'datetime', 'max_places', 'free_places', 'appointments'
        ]

    def get_appointments(self, o):
        return LeaderAppointmentSerializer(
            o.appointments.all(),
            many=True,
        ).data


class LeaderAppointmentSerializer(serializers.ModelSerializer):
    participant = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        depth = 1
        fields = [
            'id', 'creation_date', 'participant'
        ]

    def get_participant(self, o):
        return LeaderParticipantSerializer(o.participant).data


class TimeSlotSerializer(serializers.ModelSerializer):
    appointments = serializers.SerializerMethodField()

    class Meta:
        model = TimeSlot
        depth = 1
        fields = [
            'id', 'datetime', 'max_places', 'free_places', 'appointments'
        ]

    def get_appointments(self, o):
        return TimeSlotAppointmentSerializer(
            o.appointments.all(),
            many=True,
        ).data


class TimeSlotAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        depth = 1
        fields = [
            'id', 'creation_date',
        ]


class AppointmentSerializer(serializers.ModelSerializer):
    experiment = serializers.SerializerMethodField()
    participant = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        depth = 1
        fields = [
            'id', 'creation_date', 'timeslot', 'experiment', 'participant', 'start', 'end'
        ]

    def get_participant(self, o):
        return {}

    def get_experiment(self, o):
        # Local import to prevent import cycles
        from .experiment_serializers import ExperimentSerializer

        return ExperimentSerializer(
            o.experiment
        ).data
