# Generated by Django 2.0.9 on 2018-12-07 14:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('participants', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='participant',
            old_name='social_role',
            new_name='social_status',
        ),
    ]