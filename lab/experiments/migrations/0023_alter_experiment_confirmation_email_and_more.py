# Generated by Django 4.2.11 on 2024-11-14 09:09

from django.db import migrations, models
import experiments.email


class Migration(migrations.Migration):

    dependencies = [
        ("experiments", "0022_alter_experiment_confirmation_email"),
    ]

    operations = [
        migrations.AlterField(
            model_name="experiment",
            name="confirmation_email",
            field=models.TextField(
                default='<p>Beste {{parent_name}},</p>\n    <p>\n        U heeft een afspraak gemaakt om mee te doen met het experiment:\n        <strong>{{experiment_name}}</strong><br/><br/>\n        We verwachten u en {{participant_name}} op:<br/><br/>\n        Datum: <strong>{{date}}</strong><br/>\n        Tijd: <strong>{{time}} uur</strong><br/>\n        Locatie: <strong>Janskerkhof 13a</strong> (let op: dit is de groene voordeur met de helling ervoor).<br/>\n    </p>\n    <p>\n        <strong>Gezondheidsklachten</strong><br/>\n        Wij vragen u de afspraak te verzetten wanneer uw kind vlak voor de afspraak gehoorproblemen\n        en/of oorontsteking heeft en dus mogelijk minder goed hoort.\n    </p>\n    <p>\n        <strong>Aankomst in het Babylab</strong><br/>\n        Als u aanbelt bij Janskerkhof 13a en via de intercom zegt dat u voor het Babylab komt, dan wordt de deur op afstand voor u geopend.\n        Wanneer u binnenkomt, kunt u gelijk na de hal met de lift (of met de trap) naar beneden.\n        Daar vindt u aan uw rechterhand de wachtkamer, waar u plaats kunt nemen. De onderzoeksassistent zal u daar komen ophalen.\n    </p>\n    <p>\n        <strong>Het experiment</strong><br/>\n        Het experiment duurt maximaal {{experiment_duration}} minuten.\n        Omdat we ook de procedure uitleggen en er achteraf tijd is voor vragen, zult u ongeveer {{session_duration}} minuten kwijt zijn\n        aan uw bezoek aan het Babylab. In de bijlage van deze mail vindt u meer informatie over het experiment en onze werkwijze.\n    </p>\n    <p>\n        Het is belangrijk voor ons onderzoek dat er geen broertje of zusje meekomt tijdens het bezoek aan het lab.\n        Als u hierover van tevoren een andere afspraak heeft gemaakt met de assistent van het Babylab, dan geldt uiteraard die afspraak.\n    </p>\n    <p>\n        <strong>Afspraak verzetten/afzeggen</strong><br/>\n        Als u deze afspraak wilt afzeggen, kunt u dat doen via <a href="{{cancel_link}}">deze link</a>.\n        Doe dat a.u.b. minstens 24 uur van tevoren. Als u vlak van tevoren ontdekt dat u verhinderd bent,\n        neem dan contact op met de testleider ({{leader_name}}, email: babylab.ilslabs@uu.nl).\n    </p>\n    <p>\n        Meer informatie over het Babylab, bijvoorbeeld de routebeschrijving, kunt u vinden op de\n        <a href="https://babylab.wp.hum.uu.nl/">website van het Babylab</a>.\n        Wij danken u alvast hartelijk voor uw medewerking. Zonder uw deelname kunnen wij geen onderzoek doen!\n    </p>\n    <p>\n        Vriendelijke groet,<br/><br/>\n        Het team van het Babylab voor Taalonderzoek\n    </p>',
                help_text=experiments.email.AppointmentConfirmEmail.help_text,
                verbose_name="experiment:attribute:confirmation_email",
            ),
        ),
        migrations.AlterField(
            model_name="experiment",
            name="duration",
            field=models.IntegerField(verbose_name="experiment:attribute:duration"),
        ),
        migrations.AlterField(
            model_name="experiment",
            name="session_duration",
            field=models.IntegerField(verbose_name="experiment:attribute:session_duration"),
        ),
    ]
