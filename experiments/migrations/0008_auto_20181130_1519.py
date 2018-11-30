# Generated by Django 2.0.9 on 2018-11-30 15:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0007_auto_20181130_0852'),
    ]

    operations = [
        migrations.CreateModel(
            name='Criterium',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_form', models.TextField(verbose_name='criterium:attribute:name_form')),
                ('name_natural', models.TextField(verbose_name='criterium:attribute:name_natural')),
                ('values', models.TextField(verbose_name='criterium:attribute:values')),
                ('correct_value', models.TextField(verbose_name='criterium:attribute:correct_value')),
                ('message_failed', models.TextField(verbose_name='criterium:attribute:message_failed')),
                ('experiments', models.ManyToManyField(related_name='specific_criteria', to='experiments.Experiment', verbose_name='criterium:attribute:experiments')),
            ],
        ),
        migrations.AlterField(
            model_name='defaultcriteria',
            name='max_age',
            field=models.IntegerField(default=-1, help_text='default_criteria:attribute:max_age:help_text', validators=[django.core.validators.MinValueValidator(-1)], verbose_name='default_criteria:attribute:max_age'),
        ),
        migrations.AlterField(
            model_name='defaultcriteria',
            name='min_age',
            field=models.IntegerField(default=-1, help_text='default_criteria:attribute:min_age:help_text', validators=[django.core.validators.MinValueValidator(-1)], verbose_name='default_criteria:attribute:min_age'),
        ),
    ]
