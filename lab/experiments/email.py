from django.utils.translation import gettext_lazy as _

from cdh.core.mail import BaseCustomTemplateEmail, CTEVarDef


class AppointmentConfirmEmail(BaseCustomTemplateEmail):
    user_variable_defs = [
        CTEVarDef(name, _(f'experiments.email.appointmentconfirm.var.{name}'))
        for name in [
            'baby', 'experiment_name', 'date', 'time', 'experiment_location',
            'leader_name', 'leader_email', 'leader_phonenumber'
        ]
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.banner = self.subject
        self.language = 'nl'
