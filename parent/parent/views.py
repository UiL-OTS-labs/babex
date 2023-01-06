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


class SignupView(FormView):
    template_name = 'signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('signup.done')

    def form_valid(self, form):
        signup = Signup(**form.cleaned_data)
        signup.put()
        return super().form_valid(form)


class SignupDone(TemplateView):
    template_name = 'signup_done.html'
