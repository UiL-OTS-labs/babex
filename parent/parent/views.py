import json

from cdh.rest import client as rest
from django.contrib import messages
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from .forms import SignupForm
from .utils import gateway, session_required


class Signup(rest.Resource):
    class Meta:
        path = "/gateway/signup/"
        supported_operations = [rest.Operations.put]

    name = rest.TextField()
    sex = rest.TextField()
    birth_date = rest.DateField()

    parent_name = rest.TextField()
    city = rest.TextField()
    phonenumber = rest.TextField()
    phonenumber_alt = rest.TextField()
    email = rest.TextField()

    english_contact = rest.BoolField()
    newsletter = rest.BoolField()

    dyslexic_parent = rest.BoolField()
    tos_parent = rest.BoolField()
    speech_parent = rest.BoolField()
    multilingual = rest.BoolField()

    link_token = rest.TextField(null=True)
    email_verified = rest.DateTimeField(null=True, blank=True)


class SignupView(FormView):
    template_name = "signup.html"
    form_class = SignupForm
    success_url = reverse_lazy("signup.done")

    def form_valid(self, form):
        # filter out blank fields
        fields = {key: value for key, value in form.cleaned_data.items() if value}
        signup = Signup(**fields)
        signup.put()
        return super().form_valid(form)


class SignupDone(TemplateView):
    template_name = "signup_done.html"


def signup_verify(request, token):
    ok, _ = gateway(request, f"/gateway/signup/verify/{token}")
    if ok:
        return render(request, "signup_confirmed.html")
    messages.error(request, "email confrimation failed")
    return redirect("home")


@session_required
def home(request):
    # TODO: this is just an example of fetching participant data from the parent app
    ok, appointments = gateway(request, "/gateway/appointment/")
    if not ok:
        messages.error(request, "error retreiving appointment data")

    ok, survey_invites = gateway(request, "/gateway/survey_invites/")
    if not ok:
        messages.error(request, "error retreiving survey data")

    return render(request, "parent/home.html", dict(appointments=appointments, survey_invites=survey_invites))


def status(request):
    # check that the lab app is reachable
    try:
        ok, _ = gateway(request, "/gateway/")
        if not ok:
            return JsonResponse(dict(ok=False))
    except Exception:
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
    return render(request, "survey/view.html", dict(survey=survey, invite_id=invite_id))


@session_required
def survey_response_view(request):
    data = json.loads(request.body)
    invite_id = data["invite"]
    # TODO: refactor frontend conde to avoid this hack
    del data["invite"]

    ok, _ = gateway(request, f"/gateway/survey/{invite_id}/response/", data=data)
    if not ok:
        messages.error(request, "error submitting data")
        return JsonResponse(dict(ok=False))
    return JsonResponse(dict(ok=True))
