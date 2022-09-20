# Generated by Django 4.0 on 2022-09-20 08:32

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0029_remove_timeslot_datetime_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='defaultcriteria',
            name='max_age',
        ),
        migrations.RemoveField(
            model_name='defaultcriteria',
            name='min_age',
        ),
        migrations.AddField(
            model_name='defaultcriteria',
            name='max_age_days',
            field=models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='defaultcriteria',
            name='max_age_months',
            field=models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='defaultcriteria',
            name='min_age_days',
            field=models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='defaultcriteria',
            name='min_age_months',
            field=models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
