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

    # specific role for support users which behaves the same as a leader
    # that is not assigned to any experiment.
    # useful for lab support to be able to see the agenda
    is_support = models.BooleanField(_("user:attribute:is_support"), default=False)

    def __audit_repr__(self):
        return "<User: {}>".format(self.email)

    @property
    def is_leader(self):
        return self.experiments.count() > 0 or self.is_support

    def get_full_name(self):
        return self.name

    def to_json(self):
        return json.dumps({"name": self.username, "isStaff": self.is_staff, "isSupport": self.is_support})

    def __str__(self):
        if self.name:
            return self.name
        return self.username
