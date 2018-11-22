from django.db import models


class ApiGroup(models.Model):

    name = models.TextField(unique=True)


class ApiUser(models.Model):

    email = models.EmailField(unique=True)
    password = models.TextField()

    is_active = models.BooleanField(default=True)
    is_frontend_admin = models.BooleanField(default=False)

    groups = models.ManyToManyField(ApiGroup)
