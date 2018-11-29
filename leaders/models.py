from django.db import models

from api.auth.models import ApiUser


class Leader(models.Model):

    name = models.TextField()

    phonenumber = models.TextField()

    api_user = models.OneToOneField(ApiUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
