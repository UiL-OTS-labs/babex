# Generated by Django 2.0.9 on 2018-12-07 15:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0009_auto_20181204_1418'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExperimentCriterium',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('correct_value', models.TextField(verbose_name='experiment_criterium:attribute:correct_value')),
                ('message_failed', models.TextField(verbose_name='experiment_criterium:attribute:message_failed')),
            ],
        ),
        migrations.RemoveField(
            model_name='criterium',
            name='correct_value',
        ),
        migrations.RemoveField(
            model_name='criterium',
            name='experiments',
        ),
        migrations.RemoveField(
            model_name='criterium',
            name='message_failed',
        ),
        migrations.AddField(
            model_name='experimentcriterium',
            name='criterium',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiments.Criterium'),
        ),
        migrations.AddField(
            model_name='experimentcriterium',
            name='experiment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiments.Experiment'),
        ),
    ]
