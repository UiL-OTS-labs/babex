from django.db import models
from django.utils.translation import ugettext_lazy as _


class Location(models.Model):

    name = models.TextField(
        _('location:attribute:name'),
    )

    route_url = models.URLField(
        _('location:attribute:route_url'),
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name


