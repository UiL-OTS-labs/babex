# Generated by Django 2.0.9 on 2018-12-14 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apiauth', '0002_auto_20181115_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='apiuser',
            name='passwords_needs_change',
            field=models.BooleanField(default=False),
        ),
    ]
