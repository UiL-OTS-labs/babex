from datetime import datetime

from django.http import HttpResponse
from django.template import defaultfilters

from ..email import AppointmentConfirmEmail
from ..models import Experiment


def email_preview(request, template, experiment=None):
    context = {
        "date": defaultfilters.date(datetime.now(), "l d-m-Y"),
        "time": defaultfilters.date(datetime.now(), "H:i"),
        "experiment_name": "Naam experiment",
        "experiment_location": "Locatie",
        "parent_name": "Naam ouder",
        "participant_name": "Kind",
        "leader_name": "Naam proefleider",
        "leader_email": "leader@uu.nl",
        "leader_phonenumber": "064-12345678",
        "all_leaders_name_list": "Lijst van proefleiders",
        "duration": "duur",
        "task_description": "Taak omschrijving",
        "additional_instructions": "Extra instructies",
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
