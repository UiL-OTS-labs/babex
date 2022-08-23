from django.db.models.signals import post_delete
from django.dispatch import receiver

from leaders.models import Leader


# TODO: not sure if this is necessary, but keep it for now

@receiver(post_delete, sender=Leader)
def on_leader_delete(sender, instance, using, **kwargs):
    # Delete the user as well
    if instance.user:
        instance.user.delete()
