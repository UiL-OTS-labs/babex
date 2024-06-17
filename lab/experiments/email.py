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
