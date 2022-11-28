from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy

from cdh.rest import client as rest

from .forms import SignupForm


class Signup(rest.Resource):
    class Meta:
        path = '/gateway/signup/'
        supported_operations = [rest.Operations.put]

    name = rest.TextField()


class SignupView(FormView):
    template_name = 'signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('signup.done')

    def form_valid(self, form):
        signup = Signup(name=form.cleaned_data['name'])
        signup.put()
        return super().form_valid(form)


class SignupDone(TemplateView):
    template_name = 'signup_done.html'
