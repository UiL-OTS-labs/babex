# Generated by Django 4.0.7 on 2023-07-04 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('participants', '0014_remove_participant_city'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='deactivated',
            field=models.DateTimeField(null=True, verbose_name='participant:attribute:deactivated'),
        ),
    ]