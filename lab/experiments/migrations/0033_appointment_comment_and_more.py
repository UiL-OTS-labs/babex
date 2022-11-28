# Generated by Django 4.0.7 on 2022-10-19 13:40

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0032_remove_defaultcriteria_max_age_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='comment',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='defaultcriteria',
            name='max_age_days',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(28)]),
        ),
        migrations.AlterField(
            model_name='defaultcriteria',
            name='max_age_months',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='defaultcriteria',
            name='min_age_days',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(28)]),
        ),
        migrations.AlterField(
            model_name='defaultcriteria',
            name='min_age_months',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]