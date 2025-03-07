# Generated by Django 4.2.11 on 2025-02-10 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("experiments", "0024_alter_experiment_duration_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="experiment",
            name="send_reminders",
            field=models.BooleanField(
                default=True,
                help_text="experiment:attribute:send_reminders:help_text",
                verbose_name="experiment:attribute:send_reminders",
            ),
        ),
    ]
