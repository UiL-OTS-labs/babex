from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from api.auth.models import ApiUser
from main.models import User


class Leader(models.Model):

    name = models.TextField()

    phonenumber = models.TextField()

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

    @property
    def email(self):
        return self.user.email

    def is_active_leader(self) -> bool:
        if self.user.groups.filter(name=settings.LEADER_GROUP):
            return self.user.is_active

        return False

    def __str__(self):
        if not self.is_active_leader():
            return _("leader:inactive").format(self.name)

        return self.name
