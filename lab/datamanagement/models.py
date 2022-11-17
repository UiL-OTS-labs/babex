from django.db import models


class Thresholds(models.Model):
    participants_with_appointment = models.IntegerField(
        default=0
    )

    participants_without_appointment = models.IntegerField(
        default=0
    )

    participant_visibility = models.IntegerField(
        default=0
    )

    comments = models.IntegerField(
        default=0
    )

    invites = models.IntegerField(
        default=0
    )
