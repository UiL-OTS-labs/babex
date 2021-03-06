# Generated by Django 2.0.9 on 2018-11-23 10:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('apiauth', '0002_auto_20181115_1420'),
    ]

    operations = [
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('name', models.TextField()),
                ('language', models.TextField()),
                ('dyslexic', models.BooleanField()),
                ('birth_date', models.DateField()),
                ('multilingual', models.BooleanField()),
                ('phonenumber', models.TextField()),
                ('handedness', models.TextField(choices=[('left', 'participant:attribute:handedness:lefthanded'), ('right', 'participant:attribute:handedness:righthanded')])),
                ('sex', models.TextField(choices=[('M', 'participant:attribute:sex:male'), ('F', 'participant:attribute:sex:female')])),
                ('social_role', models.TextField(choices=[('student', 'participant:attribute:social_role:student'), ('other', 'participant:attribute:social_role:other')])),
                ('email_subscription', models.BooleanField(default=False)),
                ('capable', models.BooleanField(default=True)),
                ('api_user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='apiauth.ApiUser')),
            ],
        ),
        migrations.CreateModel(
            name='SecondaryEmail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='participants.Participant')),
            ],
        ),
    ]
