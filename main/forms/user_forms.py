import django.contrib.auth.forms as auth_forms
from django import forms
from django.utils.translation import gettext_lazy as _

from main.models import User


class UserCreationForm(auth_forms.UserCreationForm):
    class Meta:
        fields = ('username', 'first_name', 'last_name', 'is_supreme_admin',
                  'is_active')
        model = User
        field_classes = {
            'username': auth_forms.UsernameField
        }

    def clean_is_supreme_admin(self):
        value = self.cleaned_data['is_supreme_admin']

        print(value)

        if not value:
            if User.objects.filter(is_supreme_admin=True).count() <= 1:
                self.add_error(
                    'is_supreme_admin',
                    _("main:forms:error:no_supreme_admin")
                )

        return value


class UserUpdateForm(auth_forms.UserChangeForm):
    password = None

    class Meta:
        fields = ('username', 'first_name', 'last_name', 'is_supreme_admin',
                  'is_active')
        model = User
        field_classes = {
            'username': auth_forms.UsernameField
        }

    def clean_is_supreme_admin(self):
        value = self.cleaned_data['is_supreme_admin']

        print(value)

        if not value:
            if User.objects.filter(is_supreme_admin=True).count() <= 1:
                self.add_error(
                    'is_supreme_admin',
                    _("main:forms:error:no_supreme_admin")
                )

        return value


class LDAPUserCreationForm(forms.ModelForm):
    """Combined user form for LDAP users. This form doesn't need a separate
    update form, as it's not using Django's base forms. """
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

    def clean_is_supreme_admin(self):
        value = self.cleaned_data['is_supreme_admin']

        if not value:
            if User.objects.filter(is_supreme_admin=True).count() <= 1:
                self.add_error(
                    'is_supreme_admin',
                    _("main:forms:error:no_supreme_admin")
                )

        return value
