from django.db import models
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from experiments.models import Location


class Closing(models.Model):
    start = models.DateTimeField(_('closing:attribute:start'), db_index=True)
    end = models.DateTimeField(_('closing:attribute:end'), db_index=True)

    # SET_NULL will let us keep closings history if for some reason a location is removed
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)

    # used to indicate entire lab is closed
    is_global = models.BooleanField()

    comment = models.TextField(null=True)


class ClosingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Closing
        fields = ['id', 'start', 'end', 'is_global', 'comment', 'location',
                  'location_name']

    location_name = serializers.StringRelatedField(source='location')
    location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all(),
                                                  allow_null=True)
