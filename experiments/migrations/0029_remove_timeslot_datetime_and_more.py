# Generated by Django 4.0 on 2022-08-26 11:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leaders', '0004_alter_leader_user'),
        ('participants', '0013_auto_20220805_1151'),
        ('experiments', '0028_timeslot_end_timeslot_start_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timeslot',
            name='datetime',
        ),
        migrations.AlterField(
            model_name='experiment',
            name='confirmation_email',
            field=models.TextField(default='<p>Beste {participant_name},</p>\n    <p>\n        Je hebt een afspraak gemaakt om mee te doen met het experiment:\n        <strong>{experiment_name}</strong><br/><br/>\n        We verwachten je op:<br/><br/>\n        Datum: <strong>{date}</strong><br/>\n        Tijd: <strong>{time} uur</strong><br/>\n        Locatie: <strong>{experiment_location}</strong><br/>\n    </p>\n    <p>\n        Als je deze afspraak wilt afzeggen, kun je dat doen via\n        {cancel_link:"deze link"}.\n        Doe dat alsjeblieft minstens 24 uur vantevoren. Als je vlak vantevoren\n        ontdekt dat je verhinderd bent, neem dan svp even persoonlijk contact\n        op met de proefleider\n        ({leader_name}, email: {leader_email} tel.: {leader_phonenumber}).\n    </p>\n    <p>\n        Met vriendelijke groet,<br/>\n        het UiL OTS lab\n    </p>', help_text='experiment:attribute:confirmation_email:help_text', verbose_name='experiment:attribute:confirmation_email'),
        ),
        migrations.AlterField(
            model_name='experiment',
            name='excluded_experiments',
            field=models.ManyToManyField(blank=True, help_text='experiment:attribute:excluded_experiments:help_text', to='experiments.Experiment', verbose_name='experiment:attribute:excluded_experiments'),
        ),
        migrations.AlterField(
            model_name='experiment',
            name='invite_email',
            field=models.TextField(default='<p>Je kunt je weer opgeven voor een nieuw\n    experiment: <strong>{experiment_name}</strong>.</p>\n<p>De proefleider is <strong>{leader_name}</strong>.\n<ul>\n    <li>Duur: {duration}.</li>\n    <li>Vergoeding: {compensation}.</li>\n    <li>{task_description}</li>\n    <li>{additional_instructions}</li>\n</ul>\n\n<p>Je kunt via {link_to_subscribe:"deze link"} inschrijven.</p>\n\n<p>Bedankt!</p>\n\n<p>\nMet vriendelijke groet,<br/>\n{admin}\n</p>', help_text='experiment:attribute:invite_email:help_text', verbose_name='experiment:attribute:invite_email'),
        ),
        migrations.CreateModel(
            name='Call',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('STARTED', 'experiments:call:status:started'), ('NOREPLY', 'experiments:call:status:noreply'), ('CALLBACK', 'experiments:call:status:callback'), ('VOICEMAIL', 'experiments:call:status:voicemail'), ('EMAIL', 'experiments:call:status:email'), ('CONFIRMED', 'experiments:call:status:confirmed'), ('CANCELLED', 'experiments:call:status:cancelled')], default='STARTED', max_length=20)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('comment', models.TextField(null=True)),
                ('experiment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiments.experiment')),
                ('leader', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='leaders.leader')),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='participants.participant')),
            ],
        ),
    ]
