from django.db import models


class Experiment(models.Model):

    name = models.TextField()

    duration = models.TextField()

    compensation = models.TextField()

    additional_instructions = models.TextField()

    location = models.TextField()

    open = models.BooleanField()

    # TODO: rename this to 'public'
    visible = models.BooleanField()

    participants_visible = models.BooleanField()

    excluded_experiments = models.ManyToManyField("self")