from rest_framework import serializers

from participants.models import Participant


class ParticipantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Participant
        depth = 1
        fields = [
            'id', 'name', 'email',
        ]