from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    is_supreme_admin = models.BooleanField(default=False)

    pass

