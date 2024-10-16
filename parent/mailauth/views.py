from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import FormView

from parent.utils import gateway

from .forms import LoginForm


def link_verify(request, token):
    ok, response = gateway(request, f"/gateway/mailauth/token/{token}/")

    # upon successful authentication, the lab app should respond with a session token
    if not ok or "session_token" not in response:
        messages.error(request, response.get("reason", _("parent:error:login_failed")))
        return redirect("home")

    request.session["token"] = response["session_token"]

    if response["possible_pps"]:
        # there are multiple participants (babies) associated with the given email address,
        # ask the user to choose a specific participant
        return list_pps(request, response["possible_pps"])

    redirect_to = request.GET.get("redirect", "/overview")
    return redirect(redirect_to)


def list_pps(request, possible_pps):
    """let the parent choose which of their children is the relevant one for the current session"""
    return render(request, "mailauth/resolve.html", dict(possible_pps=possible_pps))


def resolve_pp(request, participant_id):
    """tell the lab app which participant we should refer to for the rest of the session"""
    ok, response = gateway(request, "/gateway/mailauth/set_participant/", data=dict(participant_id=int(participant_id)))
    return redirect("/overview")


class LoginFormView(FormView):
    template_name = "mailauth/login.html"
    form_class = LoginForm
    success_url = reverse_lazy("mailauth:sent")

    def form_valid(self, form):
        ok, result = gateway(self.request, "/gateway/mailauth/", data=dict(email=form.cleaned_data["email"]))
        if ok:
            self.request.session["email"] = form.cleaned_data["email"]
            return super().form_valid(form)
        messages.error(self.request, _("parent:error:login_failed"))
        return super().get(self.request)


def logout(request):
    request.session.clear()
    return redirect("/")
