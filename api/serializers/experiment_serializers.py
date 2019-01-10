from rest_framework import serializers

from experiments.models import Experiment


class ExperimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experiment
        depth = 1
        fields = [
            'id', 'name', 'duration', 'compensation', 'task_description',
            'additional_instructions', 'open', 'public', 'participants_visible',
            'location', 'leader', 'additional_leaders', 'excluded_experiments',
        ]
