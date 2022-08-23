from django.db.models.signals import post_delete
from django.dispatch import receiver

from leaders.models import Leader


@receiver(post_delete, sender=Leader)
def on_leader_delete(sender, instance, using, **kwargs):
    # Delete the api_user as well, if it's not also a participant
    if instance.api_user and not instance.api_user.is_participant:
        instance.api_user.delete()
