from django.db import models
from django.conf import settings

from api.auth.models import ApiUser


class Leader(models.Model):

    name = models.TextField()

    phonenumber = models.TextField()

    api_user = models.OneToOneField(ApiUser, on_delete=models.CASCADE)

    def is_active_leader(self) -> bool:
        if self.api_user.groups.filter(name=settings.LEADER_GROUP):
            return self.api_user.is_active

        return False

    def __str__(self):
        return self.name
