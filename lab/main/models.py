from django.contrib.auth.models import AbstractUser
from django.db import models

from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    is_ldap_account = models.BooleanField(
        _('user:is_ldap_account'),
        default=False,
    )

    # remove default django fields
    first_name = None  # type: ignore
    last_name = None  # type: ignore

    name = models.CharField(_("user:attribute:name"), max_length=150)
    phonenumber = models.TextField()

    def __audit_repr__(self):
        return "<User: {}>".format(self.email)

    @property
    def is_leader(self):
        return self.experiments.count() > 0

    def get_full_name(self):
        return self.name
