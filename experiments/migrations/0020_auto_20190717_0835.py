# Generated by Django 2.0.13 on 2019-07-17 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0019_auto_20190227_1330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='defaultcriteria',
            name='multilingual',
            field=models.CharField(choices=[('N', 'default_criteria:attribute:multilingual:no'), ('Y', 'default_criteria:attribute:multilingual:yes'), ('I', 'experiments:globals:indifferent')], default='I', max_length=1, verbose_name='default_criteria:attribute:multilingual'),
        ),
    ]
