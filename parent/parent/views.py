import datetime
import json
import logging
from operator import itemgetter

from cdh.rest import client as rest
from django.contrib import messages
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from .forms import SignupForm
from .utils import gateway, session_required

log = logging.getLogger()


class Signup(rest.Resource):
    class Meta:
        path = "/gateway/signup/"
        supported_operations = [rest.Operations.put]

    name = rest.TextField()
    sex = rest.TextField()
    birth_date = rest.DateField()
    birth_weight = rest.TextField()
    pregnancy_duration = rest.TextField()

    parent_first_name = rest.TextField()
    parent_last_name = rest.TextField()
    phonenumber = rest.TextField()
    phonenumber_alt = rest.TextField()
    email = rest.TextField()

    save_longer = rest.BoolField()
    english_contact = rest.BoolField()
    newsletter = rest.BoolField()

    dyslexic_parent = rest.TextField()
    tos_parent = rest.TextField()
    languages = rest.CollectionField(rest.StringCollection)


class SignupView(FormView):
    template_name = "signup.html"
    form_class = SignupForm
    success_url = reverse_lazy("signup.done")

    def form_valid(self, form):
        # filter out blank fields
        fields = {key: value for key, value in form.cleaned_data.items() if value is not None}
        signup = Signup(**fields)
        if signup.put(as_json=True):
            return super().form_valid(form)

        log.error("Couldn't reach server while processing signup")
        return super().get(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ok, languages = gateway(self.request, "/gateway/languages/")
        if not ok:
            raise RuntimeError("Could not fetch language list")

        choices = []
        for lang in languages:
            choices.append((lang["name"], lang["name"]))

        context["form"].fields["languages"].choices = choices
        return context


class SignupDone(TemplateView):
    template_name = "signup_done.html"


def signup_verify(request, token):
    ok, _ = gateway(request, f"/gateway/signup/verify/{token}")
    if ok:
        return render(request, "signup_confirmed.html")
    messages.error(request, "email confrimation failed")
    return redirect("home")


@session_required
def overview(request):
    ok, appointments = gateway(request, "/gateway/appointment/")
    if not ok:
        messages.error(request, "error retreiving appointment data")
        return render(request, "parent/overview.html")

    ok, survey_invites = gateway(request, "/gateway/survey_invites/")
    if not ok:
        messages.error(request, "error retreiving survey data")
        return render(request, "parent/overview.html")

    appointments = sorted(appointments, key=itemgetter("start"))
    # only show future appointments
    appointments = [a for a in appointments if a["start"].date() >= datetime.date.today()]

    return render(request, "parent/overview.html", dict(appointments=appointments, survey_invites=survey_invites))


def status(request):
    # check that the lab app is reachable
    try:
        ok, _ = gateway(request, "/gateway/")
        if not ok:
            return JsonResponse(dict(ok=False))
    except Exception:
        log.exception("Error in status check")
        return JsonResponse(dict(ok=False))

    return JsonResponse(dict(ok=True))


@session_required
def survey_view(request, invite_id):
    ok, survey_response = gateway(request, f"/gateway/survey/{invite_id}/response/")
    if ok and survey_response.get("completed") is not None:
        messages.error(request, "Survey already completed")
        return redirect("home")

    ok, survey = gateway(request, f"/gateway/survey/{invite_id}")
    if not ok:
        messages.error(request, survey["detail"])
        return redirect("home")

    ok, survey_response = gateway(request, f"/gateway/survey/{invite_id}/response/")
    if not ok:
        messages.error(request, survey["detail"])
        return redirect("home")

    return render(request, "survey/view.html", dict(survey=survey, invite_id=invite_id, response=survey_response))


@session_required
def survey_response_view(request):
    data = json.loads(request.body)
    invite_id = data["invite"]
    # TODO: refactor frontend code to avoid this hack
    del data["invite"]

    ok, _ = gateway(request, f"/gateway/survey/{invite_id}/response/", data=data)
    if not ok:
        messages.error(request, "error submitting data")
        return JsonResponse(dict(ok=False))
    return JsonResponse(dict(ok=True))


@session_required
def cancel_appointment_view(request, appointment_id):
    # TODO: handle appointment already canceled
    ok, _ = gateway(request, f"/gateway/appointment/{appointment_id}/", method="delete")
    if not ok:
        messages.error(request, "error")
        return JsonResponse(dict(ok=False))

    return render(request, "appointment/canceled.html")


@session_required
def data_management_view(request):
    return render(request, "data/home.html")


@session_required
def deactivate_view(request):
    ok, _ = gateway(request, "/gateway/deactivate/", method="post")
    if not ok:
        messages.error(request, "error")
        return redirect("data")

    # remove session token
    del request.session["token"]
    return render(request, "data/removed.html")


def home(request):
    return render(request, "parent/home.html")


def error404(request, *args, **kwargs):
    return render(request, "error/404.html", status=404)


def error500(request, *args, **kwargs):
    return render(request, "error/500.html", status=500)
