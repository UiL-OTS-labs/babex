# Generated by Django 2.0.10 on 2019-01-22 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0016_auto_20190108_1215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiment',
            name='additional_instructions',
            field=models.TextField(blank=True, verbose_name='experiment:attribute:additional_instructions'),
        ),
    ]
