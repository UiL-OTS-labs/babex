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
            'defaultcriteria', 'specific_criteria', 'use_timeslots',
            'timeslots', 'default_max_places',
        ]

    specific_criteria = serializers.SerializerMethodField(
        source='experimentcriterion_set'
    )

    timeslots = serializers.SerializerMethodField(
        source='timeslot_set'
    )

    leader = serializers.SerializerMethodField()

    additional_leaders = serializers.SerializerMethodField()

    def get_specific_criteria(self, o):
        # Local import to prevent import cycles
        from .criteria_serializers import ExperimentCriterionSerializer

        return ExperimentCriterionSerializer(
            o.experimentcriterion_set.all(),
            many=True
        ).data

    def get_timeslots(self, o):
        # Local import to prevent import cycles
        from .timeslot_serializers import TimeSlotSerializer

        return TimeSlotSerializer(
            o.timeslot_set.all(),
            many=True
        ).data

    def get_leader(self, o):
        # Local import to prevent import cycles
        from .leader_serializers import LeaderSerializer

        return LeaderSerializer(
            o.leader
        ).data

    def get_additional_leaders(self, o):
        # Local import to prevent import cycles
        from .leader_serializers import LeaderSerializer

        return LeaderSerializer(
            o.additional_leaders.all(),
            many=True,
        ).data


class LeaderExperimentSerializer(ExperimentSerializer):
    appointments = serializers.SerializerMethodField(
        source='appointments'
    )

    class Meta:
        model = Experiment
        depth = 1
        fields = [
            'id', 'name', 'duration', 'compensation', 'task_description',
            'additional_instructions', 'open', 'public', 'participants_visible',
            'location', 'leader', 'additional_leaders', 'excluded_experiments',
            'defaultcriteria', 'specific_criteria', 'use_timeslots',
            'timeslots', 'default_max_places', 'appointments',
        ]

    def get_timeslots(self, o):
        # Local import to prevent import cycles
        from .timeslot_serializers import LeaderTimeSlotSerializer

        return LeaderTimeSlotSerializer(
            o.timeslot_set.all(),
            many=True
        ).data

    def get_appointments(self, o):
        # Local import to prevent import cycles
        from .timeslot_serializers import LeaderAppointmentSerializer

        return LeaderAppointmentSerializer(
            o.appointments.all(),
            many=True
        ).data
