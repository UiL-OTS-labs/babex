# Generated by Django 4.0.7 on 2023-03-24 14:51

import secrets

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("signups", "0005_signup_created"),
    ]

    operations = [
        migrations.AddField(
            model_name="signup",
            name="email_verified",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="signup",
            name="link_token",
            field=models.CharField(default=secrets.token_urlsafe, max_length=64, unique=True),
        ),
    ]
