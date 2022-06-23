# Generated by Django 2.1.3 on 2018-11-06 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ApiUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('is_frontend_admin', models.BooleanField(default=False)),
            ],
        ),
    ]
