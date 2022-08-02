from rest_framework import serializers

from participants.models import Participant


class ParticipantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Participant
        depth = 1
        fields = [
            'id', 'name', 'email',
        ]


class LeaderParticipantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Participant
        depth = 1
        fields = [
            'id', 'name', 'email', 'phonenumber', 'language', 'multilingual',
            'birth_date', 'sex',
            'email_subscription',
        ]
