from django.db import models
from django.db.models.functions import Now

from auditlog import fields as auditlog_fields
from auditlog.enums import Event, UserType
from auditlog.utils.get_choices import get_choices_from_enum
import uil.core.fields as encrypted_models


class LogEntry(models.Model):
    class Meta:
        default_permissions = ('add',)

    event = models.TextField(
        choices=get_choices_from_enum(Event)
    )

    message = models.TextField(
        null=True,
        blank=True,
    )

    user = models.TextField(
        null=True,
        blank=True,
    )

    user_type = models.TextField(
        null=True,
        blank=True,
        choices=get_choices_from_enum(UserType),
    )

    extra = auditlog_fields.JSONField(
        null=True,
        blank=True,
    )

    # Record is the timestamp of the original entry, from Python's
    # perspective. It's encrypted to discourage tempering.
    record = encrypted_models.EncryptedDateTimeField(
        auto_now_add=True,
    )

    # DB record date is the timestamp of the original entry, from the
    # database's perspective
    db_record_date = models.DateTimeField(
        default=Now()
    )

    # Last modification if the timestamp of the last edit, from Python's
    # perspective. NOTE: this should be the same as record_date. If this
    # differs, the log was modified. (Which should NOT happen).
    last_modification = models.DateTimeField(
        auto_now=True,
    )
