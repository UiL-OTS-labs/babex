# Generated by Django 4.0.7 on 2023-01-03 10:16

from django.db import migrations, models
import experiments.email


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0038_alter_experiment_confirmation_email_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiment',
            name='confirmation_email',
            field=models.TextField(default='<p>Beste {{parent_name}},</p>\n    <p>\n        Je hebt een afspraak gemaakt om mee te doen met het experiment:\n        <strong>{{experiment_name}}</strong><br/><br/>\n        We verwachten je op:<br/><br/>\n        Datum: <strong>{{date}}</strong><br/>\n        Tijd: <strong>{{time}} uur</strong><br/>\n        Locatie: <strong>{{experiment_location}}</strong><br/>\n    </p>\n    <p>\n        Als je deze afspraak wilt afzeggen, kun je dat doen via\n        <a href="{{cancel_link}}">deze link</a>.\n        Doe dat alsjeblieft minstens 24 uur vantevoren. Als je vlak vantevoren\n        ontdekt dat je verhinderd bent, neem dan svp even persoonlijk contact\n        op met de proefleider\n        ({{leader_name}}, email: {{leader_email}} tel.: {{leader_phonenumber}}).\n    </p>\n    <p>\n        Met vriendelijke groet,<br/>\n        het UiL OTS lab\n    </p>', help_text=experiments.email.AppointmentConfirmEmail.help_text, verbose_name='experiment:attribute:confirmation_email'),
        ),
    ]