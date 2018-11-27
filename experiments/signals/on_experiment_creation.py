from django.db.models.signals import post_save
from django.dispatch import receiver

from ..models import Experiment, DefaultCriteria


@receiver(post_save, sender=Experiment)
def on_experiment_creation(sender, instance, created, *args, **kwargs):
    if created:
        c = DefaultCriteria.objects.filter(experiment=instance)

        if not c:
            o = DefaultCriteria()
            o.experiment = instance
            o.save()
