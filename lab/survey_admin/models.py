from django.db import models

from participants.models import Participant


class SurveyDefinition(models.Model):
    name = models.CharField(max_length=200)

    content = models.JSONField()


class SurveyInvite(models.Model):
    survey = models.ForeignKey(SurveyDefinition, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name="survey_invites")
    created = models.DateTimeField(auto_now_add=True)
    completed = models.DateTimeField(null=True)
