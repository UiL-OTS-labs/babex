from django.db import models
from django.utils.timezone import localdate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from experiments.models import Location


class Closing(models.Model):
    start = models.DateTimeField(_("agenda:closing:attribute:start"), db_index=True)
    end = models.DateTimeField(_("agenda:closing:attribute:end"), db_index=True)

    # SET_NULL will let us keep closings history if for some reason a location is removed
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, verbose_name=_("agenda:closing:attribute:location")
    )

    # used to indicate entire lab is closed
    is_global = models.BooleanField(_("agenda:cosing:attribute:is_global"))

    comment = models.TextField(_("agenda:cosing:attribute:comment"), null=True)

    @property
    def start_localdate(self):
        """returns only the date part of self.start, but in the local timezone"""
        return localdate(self.start)


class ClosingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Closing
        fields = ["id", "start", "end", "is_global", "comment", "location", "location_name"]

    location_name = serializers.StringRelatedField(source="location")  # type: ignore
    location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all(), allow_null=True)
