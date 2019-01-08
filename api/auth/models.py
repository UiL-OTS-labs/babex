from django.contrib.auth.hashers import check_password, make_password
from django.db import models


class ApiGroup(models.Model):

    name = models.TextField(unique=True)

    def __str__(self):
        return self.name


class ApiUser(models.Model):

    email = models.EmailField(unique=True)
    password = models.TextField()

    is_active = models.BooleanField(default=True)
    is_frontend_admin = models.BooleanField(default=False)

    passwords_needs_change = models.BooleanField(default=False)

    groups = models.ManyToManyField(ApiGroup)

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
