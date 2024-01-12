import json

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    # remove default django fields
    first_name = None  # type: ignore
    last_name = None  # type: ignore

    name = models.CharField(_("user:attribute:name"), max_length=150)
    phonenumber = models.CharField(_("user:attribute:phonenumber"), max_length=100)

    def __audit_repr__(self):
        return "<User: {}>".format(self.email)

    @property
    def is_leader(self):
        return self.experiments.count() > 0

    def get_full_name(self):
        return self.name

    def to_json(self):
        return json.dumps({"name": self.username, "isStaff": self.is_staff})

    def __str__(self):
        if self.name:
            return self.name
        return self.username
