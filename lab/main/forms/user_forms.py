import django.contrib.auth.forms as auth_forms
from django import forms

from main.models import User


class UserCreationForm(auth_forms.UserCreationForm):
    class Meta:
        fields = ("username", "name", "is_active")
        model = User
        field_classes = {"username": auth_forms.UsernameField}


class UserUpdateForm(auth_forms.UserChangeForm):
    password = None  # type: ignore

    class Meta:
        fields = ("username", "name", "is_active")
        model = User
        field_classes = {"username": auth_forms.UsernameField}


class SAMLUserCreationForm(forms.ModelForm):
    class Meta:
        fields = ("username", "name")
        model = User
