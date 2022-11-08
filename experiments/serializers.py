from rest_framework import serializers

from api.serializers.leader_serializers import LeaderSerializer
from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            'id', 'experiment', 'leader', 'participant', 'location',
            'start', 'end' ,'comment'
        ]

    experiment = serializers.StringRelatedField()  # type: ignore
    participant = serializers.SlugRelatedField('name', read_only=True)  # type: ignore

    location = serializers.ReadOnlyField()
    leader = serializers.ReadOnlyField(source='leader.name')

    start = serializers.DateTimeField()
    end = serializers.DateTimeField()

