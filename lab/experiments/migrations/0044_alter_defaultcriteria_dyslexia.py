# Generated by Django 4.0.7 on 2023-02-21 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0043_alter_appointment_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='defaultcriteria',
            name='dyslexia',
            field=models.CharField(choices=[('Y', 'default_criteria:attribute:dyslexia:yes'), ('N', 'default_criteria:attribute:dyslexia:no'), ('I', 'experiments:globals:indifferent')], default='N', max_length=1, verbose_name='default_criteria:attribute:dyslexia'),
        ),
    ]
