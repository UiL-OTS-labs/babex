# Generated by Django 4.0.7 on 2023-11-14 09:40

import cdh.core.fields.encrypted_fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('participants', '0005_remove_participant_languages_participant_languages'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='english_contact',
            field=cdh.core.fields.encrypted_fields.EncryptedBooleanField(default=False, verbose_name='participant:attribute:english_contact'),
        ),
        migrations.AddField(
            model_name='participant',
            name='save_longer',
            field=cdh.core.fields.encrypted_fields.EncryptedBooleanField(default=False, verbose_name='participant:attribute:save_longer'),
        ),
    ]
