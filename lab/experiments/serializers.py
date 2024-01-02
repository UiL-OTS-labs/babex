from rest_framework import serializers

from .models import Appointment, Experiment


class AppointmentSerializer(serializers.ModelSerializer):
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
            "instructions",
        ]

    experiment = serializers.StringRelatedField()  # type: ignore
    participant = serializers.SlugRelatedField("name", read_only=True)  # type: ignore

    location = serializers.ReadOnlyField()
    leader = serializers.ReadOnlyField(source="leader.name")

    contact_phone = serializers.ReadOnlyField(source="leader.phonenumber")

    start = serializers.DateTimeField()
    end = serializers.DateTimeField()

    instructions = serializers.ReadOnlyField(source="experiment.additional_instructions")


class ExperimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experiment
        depth = 1
        fields = [
            "id",
            "name",
            "duration",
            "task_description",
            "additional_instructions",
            "location",
            "leaders",
            "excluded_experiments",
            "defaultcriteria",
        ]
