from rest_framework import serializers

from participants.models import Participant
from main.models import User
from .models import Appointment, Experiment


class ExperimentLeadersSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = User
        fields = ["id", "name"]


class AppointmentSerializer(serializers.ModelSerializer):
    class AppointmentExperimentSerializer(serializers.ModelSerializer):
        class Meta:
            model = Experiment
            fields = ["id", "name", "leaders"]

        leaders = ExperimentLeadersSerializer(read_only=True, many=True)

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
    leader = ExperimentLeadersSerializer()

    contact_phone = serializers.ReadOnlyField(source="leader.phonenumber")

    start = serializers.DateTimeField()
    end = serializers.DateTimeField()

    session_duration = serializers.ReadOnlyField(source="experiment.session_duration")

    def update(self, instance, validated_data):
        if "leader" in validated_data:
            instance.leader = User.objects.get(pk=validated_data["leader"]["id"])
            del validated_data["leader"]
        return super().update(instance, validated_data)


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
