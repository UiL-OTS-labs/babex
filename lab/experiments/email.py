from cdh.mail.classes import BaseCustomTemplateEmail, CTEVarDef
from django.utils.translation import gettext_lazy as _


class AppointmentConfirmEmail(BaseCustomTemplateEmail):
    user_variable_defs = [
        CTEVarDef("participant_name", ""),
        CTEVarDef("experiment_name", ""),
        CTEVarDef("date", ""),
        CTEVarDef("time", ""),
        CTEVarDef("experiment_location", ""),
        CTEVarDef("leader_name", ""),
        CTEVarDef("leader_email", ""),
        CTEVarDef("leader_phonenumber", ""),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.banner = self.subject
        self.language = "nl"


DEFAULT_CONFIRMATION_MAIL = """<p>Beste {{parent_name}},</p>
    <p>
        U heeft een afspraak gemaakt om mee te doen met het experiment:
        <strong>{{experiment_name}}</strong><br/><br/>
        We verwachten u en {{participant_name}} op:<br/><br/>
        Datum: <strong>{{date}}</strong><br/>
        Tijd: <strong>{{time}} uur</strong><br/>
        Locatie: <strong>Janskerkhof 13a</strong> (let op: dit is de groene voordeur met de helling ervoor).<br/>
    </p>
    <p>
        <strong>Gezondheidsklachten</strong><br/>
        Wij vragen u de afspraak te verzetten wanneer uw kind vlak voor de afspraak gehoorproblemen
        en/of oorontsteking heeft en dus mogelijk minder goed hoort.
    </p>
    <p>
        <strong>Aankomst in het Babylab</strong><br/>
        Als u aanbelt bij Janskerkhof 13a en via de intercom zegt dat u voor het Babylab komt, dan wordt de deur op afstand voor u geopend.
        Wanneer u binnenkomt, kunt u gelijk na de hal met de lift (of met de trap) naar beneden.
        Daar vindt u aan uw rechterhand de wachtkamer, waar u plaats kunt nemen. De onderzoeksassistent zal u daar komen ophalen.
    </p>
    <p>
        <strong>Het experiment</strong><br/>
        Het experiment duurt maximaal {{experiment_duration}}.
        Omdat we ook de procedure uitleggen en er achteraf tijd is voor vragen, zult u ongeveer {{session_duration}} kwijt zijn
        aan uw bezoek aan het Babylab. In de bijlage van deze mail vindt u meer informatie over het experiment en onze werkwijze.
    </p>
    <p>
        Het is belangrijk voor ons onderzoek dat er geen broertje of zusje meekomt tijdens het bezoek aan het lab.
        Als u hierover van tevoren een andere afspraak heeft gemaakt met de assistent van het Babylab, dan geldt uiteraard die afspraak.
    </p>
    <p>
        <strong>Afspraak verzetten/afzeggen</strong><br/>
        Als u deze afspraak wilt afzeggen, kunt u dat doen via <a href="{{cancel_link}}">deze link</a>.
        Doe dat a.u.b. minstens 24 uur van tevoren. Als u vlak van tevoren ontdekt dat u verhinderd bent,
        neem dan contact op met de testleider ({{leader_name}}, email: babylab.ilslabs@uu.nl).
    </p>
    <p>
        Meer informatie over het Babylab, bijvoorbeeld de routebeschrijving, kunt u vinden op de
        <a href="https://babylab.wp.hum.uu.nl/">website van het Babylab</a>.
        Wij danken u alvast hartelijk voor uw medewerking. Zonder uw deelname kunnen wij geen onderzoek doen!
    </p>
    <p>
        Vriendelijke groet,<br/><br/>
        Het team van het Babylab voor Taalonderzoek
    </p>"""


class AppointmentReminderEmail(BaseCustomTemplateEmail):
    user_variable_defs = [
        CTEVarDef("participant_name", ""),
        CTEVarDef("experiment_name", ""),
        CTEVarDef("date", ""),
        CTEVarDef("time", ""),
        CTEVarDef("experiment_location", ""),
        CTEVarDef("leader_name", ""),
        CTEVarDef("leader_email", ""),
        CTEVarDef("leader_phonenumber", ""),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.banner = self.subject
        self.language = "nl"


DEFAULT_REMINDER_MAIL = """
    <p>
        Beste {{parent_name}},
    </p>
    <p>
        <strong>Dit is een herinnering aan uw afspraak.</strong>
    </p>
    <p>
        U heeft een afspraak gemaakt om met {{participant.name}} mee te doen aan het experiment: <strong> {{experiment_name}}</strong>.
    </p>
    <p>
        We verwachten u op: <br/>
        Datum: <strong>{{date}}</strong><br/>
        Tijd: <strong>{{time}} uur</strong><br/>
        Locatie: <strong>Janskerkhof 13a</strong> (let op: dit is de groene voordeur met de helling ervoor).<br/>
    </p>
    <p>
        <strong>Gezondheidsklachten</strong><br>
        Wij vragen u de afspraak te verzetten wanneer uw kind vlak voor de afspraak gehoorproblemen en/of oorontsteking heeft en dus mogelijk minder goed hoort.
    </p>
    <p>
        <strong>Afspraak verzetten/afzeggen</strong><br>
        Als u deze afspraak wilt afzeggen, kunt u dat doen via deze link. Doe dat a.u.b. minstens 24 uur van tevoren. Als u vlak van tevoren ontdekt dat u verhinderd bent, neem dan contact op met de testleider ({{leader_name}}, email: babylab.ilslabs@uu.nl).
    </p>
    <p>
        Meer informatie over het Babylab, bijvoorbeeld de routebeschrijving, kunt u vinden op de <a href="https://babylab.wp.hum.uu.nl/">website van het Babylab</a>. Wij danken u alvast hartelijk voor uw medewerking. Zonder uw deelname kunnen wij geen onderzoek doen!



    </p>
    <p>
        Vriendelijke groet,<br><br>
        Het team van het Babylab voor Taalonderzoek
    </p>
"""
