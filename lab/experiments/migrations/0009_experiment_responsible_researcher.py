# Generated by Django 4.0.7 on 2024-02-15 09:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("experiments", "0008_experiment_session_duration"),
    ]

    operations = [
        migrations.AddField(
            model_name="experiment",
            name="responsible_researcher",
            field=models.TextField(default="", verbose_name="experiment:attribute:responsible_researcher"),
            preserve_default=False,
        ),
    ]
