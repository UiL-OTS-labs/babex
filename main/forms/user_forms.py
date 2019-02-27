import django.contrib.auth.forms as auth_forms
from django import forms

from main.models import User


class UserCreationForm(auth_forms.UserCreationForm):
    class Meta:
        fields = ('username', 'first_name', 'last_name', 'is_supreme_admin',
                  'is_active')
        model = User
        field_classes = {
            'username': auth_forms.UsernameField
        }


class LDAPUserCreationForm(forms.ModelForm):
    class Meta:
        fields = ('username', 'is_supreme_admin',
                  'is_active')
        model = User
        field_classes = {
            'username': auth_forms.UsernameField
        }

    def __init__(self, *args, **kwargs):
        super(LDAPUserCreationForm, self).__init__(*args, **kwargs)

        # Rename fields
        self.fields['username'].label = "Solis-ID"
        self.fields['username'].help_text = ""
