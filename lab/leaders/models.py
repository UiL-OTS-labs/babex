from django.db import models


class Leader(models.Model):
    """Used to prevent errors from old migrations trying to access leaders.Leader"""
    pass
