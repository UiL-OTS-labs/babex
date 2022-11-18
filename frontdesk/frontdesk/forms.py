from django import forms

from cdh.core.forms import TemplatedForm


class SignupForm(TemplatedForm):
    name = forms.CharField()
