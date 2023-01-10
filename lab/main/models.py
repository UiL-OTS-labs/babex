from django.contrib.auth.models import AbstractUser
from django.db import models

from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    is_ldap_account = models.BooleanField(
        _('user:is_ldap_account'),
        default=False,
    )

    phonenumber = models.TextField()

    def __audit_repr__(self):
        return "<AdminUser: {}>".format(self.email)

    @property
    def is_leader(self):
        return self.experiments.count() > 0

    @property
    def name(self):
        # reuse the existing fields on User, although it would
        # probably be better to have just a plain `name` field
        return ' '.join(self.first_name, self.last_name)
