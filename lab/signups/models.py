from django.db import models


class Signup(models.Model):
    name = models.CharField(max_length=100)
