from django.db import models


class SurveyDefinition(models.Model):
    name = models.CharField(max_length=200)

    content = models.JSONField()
