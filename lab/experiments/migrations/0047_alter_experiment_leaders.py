# Generated by Django 4.0.7 on 2023-06-12 08:27

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('experiments', '0046_appointment_updated_alter_appointment_outcome'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiment',
            name='leaders',
            field=models.ManyToManyField(help_text='experiment:attribute:leaders:help_text', related_name='experiments', to=settings.AUTH_USER_MODEL, verbose_name='experiment:attribute:leaders'),
        ),
    ]