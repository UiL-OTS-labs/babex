# Generated by Django 4.0.7 on 2023-04-17 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey_admin', '0002_surveyresponse_completed_surveyresponse_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='surveyresponse',
            name='page',
            field=models.IntegerField(default=0),
        ),
    ]
