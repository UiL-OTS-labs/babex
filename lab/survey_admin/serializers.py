from rest_framework import serializers

from .models import SurveyDefinition, SurveyInvite, SurveyResponse


class SurveyDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyDefinition
        fields = "__all__"


class SurveyInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyInvite
        fields = "__all__"

    survey_name = serializers.CharField(source="survey.name")


class SurveyResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyResponse
        fields = ["data", "created", "updated", "completed", "page"]
