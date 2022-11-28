# Generated by Django 2.0.13 on 2019-04-23 09:56

import auditlog.fields
from django.db import migrations, models
from  django.db.models.functions import Now
import cdh.core.fields.encrypted_fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.TextField(choices=[('LOGIN', 'login'), ('LOGOUT', 'logout'), ('UNCATEGORISED', 'uncategorised')])),
                ('message', models.TextField(blank=True, null=True)),
                ('user', models.TextField(blank=True, null=True)),
                ('user_type', models.TextField(blank=True, choices=[('SYSTEM', 'system'), ('ADMIN', 'admin'), ('LEADER', 'leader'), ('PARTICIPANT', 'participant')], null=True)),
                ('extra', auditlog.fields.JSONField(blank=True, null=True)),
                ('record',
                 cdh.core.fields.encrypted_fields.EncryptedDateTimeField(
                    auto_now_add=True)),
                ('db_record_date', models.DateTimeField(default=Now())),
                ('last_modification', models.DateTimeField(auto_now=True)),
            ],
            options={
                'default_permissions': ('add',),
            },
        ),
    ]