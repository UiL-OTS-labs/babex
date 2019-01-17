from rest_framework import serializers

from experiments.models import ExperimentCriterium


class ExperimentCriteriumSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperimentCriterium
        fields = [
            'id', 'criterium', 'correct_value', 'message_failed'
        ]
        depth = 1
