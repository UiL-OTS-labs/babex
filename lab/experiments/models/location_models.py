from django.db import models
from django.utils.translation import gettext_lazy as _


class Location(models.Model):

    name = models.TextField(
        _("location:attribute:name"),
    )

    route_url = models.URLField(
        _("location:attribute:route_url"),
        blank=True,
        null=True,
    )

    # when set to False, "entire building" closings will not affect this location
    part_of_building = models.BooleanField(default=True)

    def __str__(self):
        return self.name
