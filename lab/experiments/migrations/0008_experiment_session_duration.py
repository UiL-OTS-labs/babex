# Generated by Django 4.0.7 on 2024-01-23 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0007_alter_experiment_invite_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='session_duration',
            field=models.TextField(default='', verbose_name='experiment:attribute:session_duration'),
            preserve_default=False,
        ),
    ]
