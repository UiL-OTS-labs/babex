from django.shortcuts import render
from django.contrib import messages
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy

from cdh.rest import client as rest

from .forms import SignupForm
from .utils import gateway, session_required


class Signup(rest.Resource):
    class Meta:
        path = "/gateway/signup/"
        supported_operations = [rest.Operations.put]

    name = rest.TextField()


class SignupView(FormView):
    template_name = "signup.html"
    form_class = SignupForm
    success_url = reverse_lazy("signup.done")

    def form_valid(self, form):
        signup = Signup(name=form.cleaned_data["name"])
        signup.put()
        return super().form_valid(form)


class SignupDone(TemplateView):
    template_name = "signup_done.html"


@session_required
def home(request):
    # TODO: this is just an example of fetching participant data from the parent app
    ok, appointments = gateway(request, "/gateway/appointment/")
    if not ok:
        messages.error(request, "error retreiving data")

    return render(request, "parent/home.html", dict(appointments=appointments))
