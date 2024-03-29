# Generated by Django 4.0.7 on 2023-10-31 13:35

import cdh.core.fields.encrypted_fields
from django.db import migrations

import signups.models


class Migration(migrations.Migration):
    dependencies = [
        ("signups", "0002_rename_parent_name_signup_parent_first_name_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="signup",
            name="multilingual",
        ),
        migrations.AddField(
            model_name="signup",
            name="languages",
            field=signups.models.EncryptedJSONListField(null=True),
        ),
        migrations.AddField(
            model_name="signup",
            name="tos_parent",
            field=cdh.core.fields.encrypted_fields.EncryptedCharField(null=True),
        ),
    ]
