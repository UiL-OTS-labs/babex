from rest_framework import serializers

from .models import SurveyDefinition, SurveyInvite


class SurveyDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyDefinition
        fields = "__all__"


class SurveyInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyInvite
        fields = "__all__"

    survey_name = serializers.CharField(source="survey.name")
