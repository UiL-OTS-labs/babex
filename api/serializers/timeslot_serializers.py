from rest_framework import serializers

from experiments.models import TimeSlot, Appointment


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        depth = 1
        fields = [
            'id', 'datetime', 'max_places', 'free_places'
        ]


class AppointmentSerializer(serializers.ModelSerializer):
    experiment = serializers.SerializerMethodField()
    participant = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        depth = 1
        fields = [
            'id', 'creation_date', 'timeslot', 'experiment', 'participant'
        ]

    def get_participant(self, o):
        return {}

    def get_experiment(self, o):
        # Local import to prevent import cycles
        from .experiment_serializers import ExperimentSerializer

        return ExperimentSerializer(
            o.timeslot.experiment
        ).data
