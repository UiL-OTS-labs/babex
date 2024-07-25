from datetime import datetime, timedelta

import cdh.files.db
from django.db import models
from django.urls import reverse
from django.utils.timezone import get_current_timezone
from django.utils.translation import gettext_lazy as _

from main.models import User

from ..email import AppointmentConfirmEmail
from .default_criteria_models import DefaultCriteria
from .location_models import Location


def _get_dt_2_hours_ago() -> datetime:
    return datetime.now(tz=get_current_timezone()) - timedelta(hours=2)


class Experiment(models.Model):
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
        neem dan contact op met de proefleider ({{leader_name}}, email: babylab.ilslabs@uu.nl tel.: {{leader_phonenumber}}).
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

    DEFAULT_INVITE_MAIL = ""

    name = models.TextField(_("experiment:attribute:name"))

    duration = models.TextField(_("experiment:attribute:duration"))

    session_duration = models.TextField(_("experiment:attribute:session_duration"))

    # how many participants are aimed for
    recruitment_target = models.PositiveIntegerField(
        _("experiment:attribute:recruitment_target"),
        help_text=_("experiment:attribute:recruitment_target:help"),
        default=0,
    )

    task_description = models.TextField(_("experiment:attribute:task_description"))

    additional_instructions = models.TextField(
        _("experiment:attribute:additional_instructions"),
        blank=True,
    )

    confirmation_email = models.TextField(
        _("experiment:attribute:confirmation_email"),
        help_text=AppointmentConfirmEmail.help_text,
        default=DEFAULT_CONFIRMATION_MAIL,
    )

    invite_email = models.TextField(
        _("experiment:attribute:invite_email"),
        help_text=_("experiment:attribute:invite_email:help_text"),
        default=DEFAULT_INVITE_MAIL,
    )

    location = models.ForeignKey(
        Location,
        verbose_name=_("experiment:attribute:location"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    excluded_experiments = models.ManyToManyField(
        "self",
        verbose_name=_("experiment:attribute:excluded_experiments"),
        blank=True,
        help_text=_("experiment:attribute:excluded_experiments:help_text"),
    )

    required_experiments = models.ManyToManyField(
        "self",
        verbose_name=_("experiment:attribute:required_experiments"),
        blank=True,
        help_text=_("experiment:attribute:required_experiments:help_text"),
    )

    leaders = models.ManyToManyField(
        User,
        verbose_name=_("experiment:attribute:leaders"),
        related_name="experiments",
        blank=False,
        help_text=_("experiment:attribute:leaders:help_text"),
    )

    responsible_researcher = models.TextField(_("experiment:attribute:responsible_researcher"))

    defaultcriteria = models.OneToOneField(DefaultCriteria, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        """Run models.save but make sure the experiment has default criteria"""
        try:
            no_createria = self.defaultcriteria is None
            if no_createria:
                self.defaultcriteria = DefaultCriteria.objects.create()
        except Experiment.defaultcriteria.RelatedObjectDoesNotExist:
            self.defaultcriteria = DefaultCriteria.objects.create()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def leader_names(self):
        # TODO: i18n? (for connective 'en' -> 'and')
        leader_names = [leader.name for leader in self.leaders.all()]
        return "".join(f"{name}, " for name in leader_names[:-2]) + " en ".join(leader_names[-2:])

    def is_leader(self, user: User) -> bool:
        return user.experiments.filter(pk=self.pk).exists()


class ConfirmationMailAttachment(models.Model):
    filename = models.CharField(max_length=255)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name="attachments")
    created = models.DateTimeField(auto_now_add=True)
    file = cdh.files.db.FileField()

    @property
    def link(self):
        return reverse(
            "experiments:attachment",
            args=(
                self.experiment.pk,
                self.pk,
            ),
        )
