# Generated by Django 4.0.7 on 2023-09-05 14:35

import cdh.core.fields.encrypted_fields
from django.db import migrations, models
import secrets


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Signup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', cdh.core.fields.encrypted_fields.EncryptedCharField()),
                ('sex', cdh.core.fields.encrypted_fields.EncryptedCharField()),
                ('birth_date', cdh.core.fields.encrypted_fields.EncryptedDateField()),
                ('parent_name', cdh.core.fields.encrypted_fields.EncryptedTextField()),
                ('phonenumber', cdh.core.fields.encrypted_fields.EncryptedTextField()),
                ('phonenumber_alt', cdh.core.fields.encrypted_fields.EncryptedTextField(blank=True)),
                ('email', cdh.core.fields.encrypted_fields.EncryptedTextField()),
                ('english_contact', cdh.core.fields.encrypted_fields.EncryptedBooleanField()),
                ('newsletter', cdh.core.fields.encrypted_fields.EncryptedBooleanField()),
                ('dyslexic_parent', cdh.core.fields.encrypted_fields.EncryptedCharField()),
                ('multilingual', cdh.core.fields.encrypted_fields.EncryptedBooleanField()),
                ('birth_weight', cdh.core.fields.encrypted_fields.EncryptedIntegerField(verbose_name='participant:attribute:birth_weight')),
                ('pregnancy_weeks', cdh.core.fields.encrypted_fields.EncryptedIntegerField(verbose_name='participant:attribute:pregnancy_weeks')),
                ('pregnancy_days', cdh.core.fields.encrypted_fields.EncryptedIntegerField(verbose_name='participant:attribute:pregnancy_days')),
                ('status', models.CharField(choices=[('NEW', 'signups:stats:new'), ('APPROVED', 'signups:stats:approved'), ('REJECTED', 'signups:stats:rejected')], default='NEW', max_length=20)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('email_verified', models.DateTimeField(blank=True, null=True)),
                ('link_token', models.CharField(default=secrets.token_urlsafe, max_length=64, unique=True)),
            ],
        ),
    ]
