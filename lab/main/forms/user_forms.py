import django.contrib.auth.forms as auth_forms
from django import forms

from main.models import User


class UserCreationForm(auth_forms.UserCreationForm):
    class Meta:
        fields = ('username', 'name', 'is_active')
        model = User
        field_classes = {
            'username': auth_forms.UsernameField
        }


class UserUpdateForm(auth_forms.UserChangeForm):
    password = None  # type: ignore

    class Meta:
        fields = ('username', 'name', 'is_active')
        model = User
        field_classes = {
            'username': auth_forms.UsernameField
        }


class LDAPUserCreationForm(forms.ModelForm):
    """Combined user form for LDAP users. This form doesn't need a separate
    update form, as it's not using Django's base forms. """
    class Meta:
        fields = ('username', 'is_active')
        model = User
        field_classes = {
            'username': auth_forms.UsernameField
        }

    def __init__(self, *args, **kwargs):
        super(LDAPUserCreationForm, self).__init__(*args, **kwargs)

        # Rename fields
        self.fields['username'].label = "Solis-ID"
        self.fields['username'].help_text = ""
