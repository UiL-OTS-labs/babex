from rest_framework import serializers

from participants.models import Participant
from .models import Appointment, Experiment


class AppointmentSerializer(serializers.ModelSerializer):
    class AppointmentExperimentSerializer(serializers.ModelSerializer):
        class Meta:
            model = Experiment
            fields = ["id", "name"]

    class AppointmentParticipantSerializer(serializers.ModelSerializer):
        class Meta:
            model = Participant
            fields = ["id", "name"]

    class Meta:
        model = Appointment
        fields = [
            "id",
            "experiment",
            "leader",
            "participant",
            "location",
            "start",
            "end",
            "comment",
            "outcome",
            "contact_phone",
            "session_duration",
        ]

    experiment = AppointmentExperimentSerializer(read_only=True)
    participant = AppointmentParticipantSerializer(read_only=True)

    location = serializers.ReadOnlyField()
    leader = serializers.ReadOnlyField(source="leader.name")

    contact_phone = serializers.ReadOnlyField(source="leader.phonenumber")

    start = serializers.DateTimeField()
    end = serializers.DateTimeField()

    session_duration = serializers.ReadOnlyField(source="experiment.session_duration")


class ExperimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experiment
        depth = 1
        fields = [
            "id",
            "name",
            "duration",
            "task_description",
            "location",
            "leaders",
            "excluded_experiments",
            "defaultcriteria",
        ]
