# Generated by Django 2.0.13 on 2019-10-08 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0020_auto_20190717_0835'),
    ]

    operations = [
        migrations.AlterField(
            model_name='defaultcriteria',
            name='multilingual',
            field=models.CharField(choices=[('N', 'default_criteria:attribute:multilingual:no'), ('Y', 'default_criteria:attribute:multilingual:yes'), ('I', 'experiments:globals:indifferent')], default='N', max_length=1, verbose_name='default_criteria:attribute:multilingual'),
        ),
    ]