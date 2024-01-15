from datetime import datetime

from django.http import HttpResponse
from django.template import defaultfilters
from django.utils.translation import gettext_lazy as _

from ..email import AppointmentConfirmEmail
from ..models import Experiment


def email_preview(request, template, experiment=None):
    context = {
        "date": defaultfilters.date(datetime.now(), "l d-m-Y"),
        "time": defaultfilters.date(datetime.now(), "H:i"),
        "experiment_name": _("experiments:views:email_preview:experiment_name"),
        "experiment_location": _("experiments:views:email_preview:location"),
        "parent_name": _("experiments:views:email_preview:parent_name"),
        "leader_name": _("experiments:views:email_preview:leader_name"),
        "leader_email": "leader@uu.nl",
        "leader_phonenumber": "064-12345678",
        "all_leaders_name_list": _("experiments:views:email_preview:leader_names"),
        "duration": _("experiments:views:email_preview:duration"),
        "task_description": _("experiments:views:email_preview:task_description"),
        "additional_instructions": _("experiments:views:email_preview:additional_instructions"),
    }

    if experiment is not None:
        experiment = Experiment.objects.get(pk=experiment)
        context["experiment_location"] = experiment.location.name
        context["experiment_name"] = experiment.name
        context["duration"] = experiment.duration
        context["additional_instructions"] = experiment.additional_instructions

    email_kwargs = {
        "to": "example@example.org",
        "subject": "Test Email",
        "contents": request.POST.get("contents", None),
        "sender": request.POST.get("sender", None),
        "banner": request.POST.get("banner", None),
        "footer": request.POST.get("footer", None),
        "context": context,
    }

    if template == "confirmation":
        msg = AppointmentConfirmEmail(**email_kwargs)
        return HttpResponse(msg.render_preview())
