from cdh.core.mail import BaseCustomTemplateEmail, CTEVarDef
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string


class AppointmentConfirmEmail(BaseCustomTemplateEmail):
    user_variable_defs = [
        CTEVarDef("baby", _("experiments.email.appointmentconfirm.var.baby")),
        CTEVarDef("experiment_name", _("experiments.email.appointmentconfirm.var.experiment_name")),
        CTEVarDef("date", _("experiments.email.appointmentconfirm.var.date")),
        CTEVarDef("time", _("experiments.email.appointmentconfirm.var.time")),
        CTEVarDef("experiment_location", _("experiments.email.appointmentconfirm.var.experiment_location")),
        CTEVarDef("leader_name", _("experiments.email.appointmentconfirm.var.leader_name")),
        CTEVarDef("leader_email", _("experiments.email.appointmentconfirm.var.leader_email")),
        CTEVarDef("leader_phonenumber", _("experiments.email.appointmentconfirm.var.leader_phonenumber")),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.banner = self.subject
        self.language = "nl"
        self.footer = render_to_string("mail/footer.html")
