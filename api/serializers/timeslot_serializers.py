from rest_framework import serializers

from experiments.models import TimeSlot


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        depth = 1
        fields = [
            'id', 'datetime', 'max_places', 'free_places'
        ]
