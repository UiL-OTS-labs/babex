from django import forms

from cdh.core.forms import TemplatedForm


class LoginForm(TemplatedForm):
    email = forms.EmailField(label="E-mail")
