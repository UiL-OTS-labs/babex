# Generated by Django 2.0.9 on 2018-12-20 14:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('participants', '0006_auto_20181218_1227'),
        ('experiments', '0014_invitation'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='invitation',
            unique_together={('experiment', 'participant')},
        ),
    ]
