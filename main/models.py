from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_supreme_admin = models.BooleanField(default=False)

    pass

