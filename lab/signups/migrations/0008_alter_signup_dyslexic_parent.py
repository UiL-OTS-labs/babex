# Generated by Django 4.0.7 on 2023-07-27 14:10

import cdh.core.fields.encrypted_fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('signups', '0007_remove_signup_city_remove_signup_speech_parent_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signup',
            name='dyslexic_parent',
            field=cdh.core.fields.encrypted_fields.EncryptedCharField(),
        ),
    ]
