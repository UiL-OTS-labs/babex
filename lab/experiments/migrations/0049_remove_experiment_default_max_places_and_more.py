# Generated by Django 4.0.7 on 2023-06-22 08:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0048_experiment_required_experiments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='experiment',
            name='default_max_places',
        ),
        migrations.RemoveField(
            model_name='timeslot',
            name='max_places',
        ),
    ]