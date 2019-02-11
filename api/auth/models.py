import uuid
from datetime import datetime

from django.contrib.auth.hashers import check_password, make_password
from django.db import models

from django.conf import settings
from pytz import timezone


class ApiGroup(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name


class ApiUser(models.Model):
    email = models.EmailField(unique=True)
    password = models.TextField()

    is_active = models.BooleanField(default=True)
    is_frontend_admin = models.BooleanField(default=False)

    passwords_needs_change = models.BooleanField(default=False)

    groups = models.ManyToManyField(ApiGroup)

    @property
    def is_leader(self):
        return hasattr(self, 'leader')

    @property
    def is_participant(self):
        return hasattr(self, 'participant')

    @property
    def has_password(self) -> bool:
        return self.password is not None and self.password != ''

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """
        Return a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """

        def setter(raw_password):
            self.set_password(raw_password)
            self.save(update_fields=["password"])

        return check_password(raw_password, self.password, setter)

    def __str__(self):
        return self.email


def _get_date_2hours():
    tz = timezone(settings.TIME_ZONE)
    dt = datetime.now(tz)
    hour = dt.hour + 2
    return dt.replace(hour=hour)


class UserToken(models.Model):

    PASSWORD_RESET = 'P'
    MAILINGLIST_UNSUBSCRIBE = 'M'
    CANCEL_APPOINTMENTS = 'C'

    TYPES = (
        (PASSWORD_RESET, 'Password Reset'),
        (MAILINGLIST_UNSUBSCRIBE, 'Mailinglist unsubscribe'),
        (CANCEL_APPOINTMENTS, 'Cancel appointments')
    )

    user = models.ForeignKey(
        ApiUser,
        on_delete=models.CASCADE,
        null=True,
    )

    participant = models.ForeignKey(
        'participants.Participant',
        on_delete=models.CASCADE,
        null=True,
    )

    token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
    )

    type = models.CharField(
        choices=TYPES,
        max_length=1,
    )

    expiration = models.DateTimeField(
        editable=False,
        default=_get_date_2hours
    )

    def is_valid(self) -> bool:
        tz = timezone(settings.TIME_ZONE)
        now = datetime.now(tz)

        return self.expiration > now
