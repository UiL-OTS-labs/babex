# Generated by Django 2.0.13 on 2019-04-15 11:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0006_auto_20181214_1024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='experiment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='experiments.Experiment', verbose_name='comment:attribute:experiment'),
        ),
        migrations.AddField(
            model_name='comment',
            name='system_comment',
            field=models.BooleanField(default=False, verbose_name='comment:attribute:datetime'),
        ),
    ]