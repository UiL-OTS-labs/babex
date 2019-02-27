from django.contrib.auth.models import AbstractUser
from django.db import models

from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    is_supreme_admin = models.BooleanField(
        _('user:is_supreme_admin'),
        default=False,
    )

    is_ldap_account = models.BooleanField(
        _('user:is_ldap_account'),
        default=False,
    )
