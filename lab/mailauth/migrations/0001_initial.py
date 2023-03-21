# Generated by Django 4.0.7 on 2023-02-23 12:33

import cdh.core.fields.encrypted_fields
from django.db import migrations, models
import django.db.models.deletion
import secrets


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('participants', '0013_auto_20220805_1151'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailAuth',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', cdh.core.fields.encrypted_fields.EncryptedEmailField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('expiry', models.DateTimeField()),
                ('link_token', models.CharField(default=secrets.token_urlsafe, max_length=64, unique=True)),
                ('session_token', models.CharField(max_length=64, null=True, unique=True)),
                ('participant', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='participants.participant')),
            ],
        ),
    ]
