from django.db import models


class EncryptedManager(models.Manager):
    """Provides helper methods for facilitating queries with encrypted fields"""

    def efilter(self, **kwargs):
        """Iterate through model objects that match filters given in kwargs.
        Differs from django's filter in two important ways:
        1. Only direct equality comparisons are supported
        2. Returns results in a generator instead of QuerySet
        """
        for object in self.all():
            for field, value in kwargs.items():
                if getattr(object, field) != value:
                    break
            else:
                yield object
