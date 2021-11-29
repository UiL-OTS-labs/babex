from django.db.models.signals import pre_delete
from django.dispatch import receiver

from participants.models import Participant


@receiver(pre_delete, sender=Participant)
def on_participant_delete(sender, instance, using, **kwargs):
    # Delete the api_user as well, if it's not also a leader
    if instance.api_user and not instance.api_user.is_leader:
        instance.api_user.delete()
