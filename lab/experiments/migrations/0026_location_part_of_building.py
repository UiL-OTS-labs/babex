# Generated by Django 4.2.11 on 2025-02-28 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("experiments", "0025_experiment_send_reminders"),
    ]

    operations = [
        migrations.AddField(
            model_name="location",
            name="part_of_building",
            field=models.BooleanField(default=True),
        ),
    ]
