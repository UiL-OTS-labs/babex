from rest_framework import serializers

from experiments.models import ExperimentCriterion


class ExperimentCriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperimentCriterion
        fields = [
            'id', 'criterion', 'correct_value', 'message_failed'
        ]
        depth = 1
