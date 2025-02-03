import datetime
import json
import logging

from django.contrib import messages
from django.http.response import JsonResponse
from django.utils.safestring import mark_safe
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from .forms import SignupForm
from .utils import gateway, session_required

log = logging.getLogger()


class SignupView(FormView):
    template_name = "signup.html"
    form_class = SignupForm
    success_url = reverse_lazy("signup.done")

    # need to pass the CSP nonce from the view to form widgets
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["csp_nonce"] = str(self.request.csp_nonce) if hasattr(self.request, "csp_nonce") else ""
        return kwargs

    def form_valid(self, form):
        # filter out blank fields
        fields = {key: value for key, value in form.cleaned_data.items() if value is not None}
        fields["birth_date"] = fields["birth_date"].isoformat()
        ok, result = gateway(self.request, "/gateway/signup/", data=fields)
        if ok:
            self.request.session["email"] = form.cleaned_data["email"]
            return super().form_valid(form)

        log.error("Couldn't reach server while processing signup")
        return super().get(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ok, languages = gateway(self.request, "/gateway/languages/")
        if not ok:
            raise RuntimeError("Could not fetch language list")

        choices = []
        language_names = sorted(set(lang["name"] for lang in languages))
        for language in language_names:
            choices.append((language, language))

        # append any new languages the user may have typed in but are not yet saved in the backend
        # (for when the form is invalid and we want to refill the form)
        for language in context["form"].data.getlist("languages"):
            if language not in language_names:
                choices.append((language, language))

        context["form"].fields["languages"].choices = choices
        return context


class SignupDone(TemplateView):
    template_name = "signup_done.html"


def signup_verify(request, token):
    ok, result = gateway(request, f"/gateway/signup/verify/{token}")
    if ok:
        return render(request, "signup_confirmed.html")
    messages.error(request, mark_safe(result.get("reason", _("parent:error:signup_verify"))))
    return redirect("home")


@session_required
def overview(request):
    ok, appointments = gateway(request, "/gateway/appointment/")
    if not ok:
        messages.error(request, _("parent:error:data_generic"))
        return render(request, "parent/overview.html")

    ok, survey_invites = gateway(request, "/gateway/survey_invites/")
    if not ok:
        messages.error(request, _("parent:error:data_generic"))
        return render(request, "parent/overview.html")

    # sorting by outcome is a simple way to push canceled appointments to the bottom of the list
    appointments = sorted(appointments, key=lambda a: (a["outcome"] is not None, a["start"]))
    # only show future appointments
    appointments = [a for a in appointments if a["start"].date() >= datetime.date.today()]

    return render(request, "parent/overview.html", dict(appointments=appointments, survey_invites=survey_invites))


def status(request):
    # check that the lab app is reachable
    try:
        ok, result = gateway(request, "/gateway/")
        if not ok:
            return JsonResponse(dict(ok=False))
    except Exception:
        log.exception("Error in status check")
        return JsonResponse(dict(ok=False))

    return JsonResponse(dict(ok=True))


@ensure_csrf_cookie
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

    ok, result = gateway(request, f"/gateway/survey/{invite_id}/response/", data=data)
    if not ok:
        messages.error(request, _("parent:error:data_generic"))
        return JsonResponse(dict(ok=False))
    return JsonResponse(dict(ok=True))


@session_required
def cancel_appointment_view(request, appointment_id):
    ok, appointment = gateway(request, f"/gateway/appointment/{appointment_id}/")
    if not ok:
        messages.error(request, _("parent:error:data_generic"))
        return render(request, "parent/overview.html")

    if appointment["outcome"] == "CANCELED":
        # appointment already canceled
        return render(request, "appointment/canceled.html", dict(appointment=appointment))

    ok, result = gateway(request, f"/gateway/appointment/{appointment_id}/", method="delete")
    if not ok:
        messages.error(request, _("parent:error:appointment_cancel"))
        return JsonResponse(dict(ok=False))

    return render(request, "appointment/canceled.html", dict(appointment=appointment))


@session_required
def data_management_view(request):
    ok, result = gateway(request, "/gateway/session/")
    return render(request, "data/home.html", dict(name=result["name"]))


@session_required
def deactivate_view(request):
    ok, result = gateway(request, "/gateway/deactivate/", method="post")
    if not ok:
        messages.error(request, _("parent:error:deactivate"))
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
