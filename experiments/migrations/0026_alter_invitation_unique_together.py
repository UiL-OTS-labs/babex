# Generated by Django 3.2.13 on 2022-05-16 09:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0025_experiment_invite_email'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='invitation',
            unique_together=set(),
        ),
    ]
