from django import forms
from django.utils.translation import ugettext_lazy as _

from api.auth.models import ApiUser
from .models import Leader


def _clean_confirm_password(self):
    """Verifies that both passwords are equal"""
    password = self.cleaned_data['password']
    confirm_password = self.cleaned_data['confirm_password']

    if password != confirm_password:
        raise forms.ValidationError(
            _('leader:form:password:error:not_equal'))

    # If we have confirmed the password, we can discard the value
    return ''


class LeaderCreateForm(forms.Form):
    """This form is meant for creating Leaders

    We're using a regular form, as the info for Leaders are spread over multiple
    models.
    """
    name = forms.Field(
        label=_('leader:form:name'),
    )

    email = forms.EmailField(
        label=_('leader:form:email'),
    )

    phonenumber = forms.Field(
        label=_('leader:form:phonenumber'),
    )

    password = forms.Field(
        label=_('leader:form:password'),
        help_text=_('leader:form:password:help_text'),
        required=False,
        widget=forms.PasswordInput,
    )

    confirm_password = forms.Field(
        label=_('leader:form:confirm_password:label'),
        help_text=_('leader:form:confirm_password:help_text'),
        required=False,
        widget=forms.PasswordInput,
    )

    notify_user = forms.BooleanField(
        label=_('leaders:forms:create_form:notify_user:label'),
        help_text=_('leaders:forms:create_form:notify_user:help_text'),
        required=False,  # Bit of a misnomer, it means False is a valid value
        initial=True,
    )

    def clean_email(self):
        """This clean method ensures that we do not create new leaders with
                    existing emails.
                    """
        data = self.cleaned_data['email']

        existing_user = ApiUser.objects.get_by_email(data)

        if existing_user:
            raise forms.ValidationError(
                _('leader:form:email:error:user_exists'))

        return data

    def clean_confirm_password(self):
        return _clean_confirm_password(self)


class LDAPLeaderCreateForm(forms.Form):
    """This form is meant for creating Leaders

    We're using a regular form, as the info for Leaders are spread over multiple
    models.
    """

    name = forms.Field(
        label=_('leader:form:name'),
    )

    email = forms.EmailField(
        label=_('leader:form:email'),
    )

    phonenumber = forms.Field(
        label=_('leader:form:phonenumber'),
    )

    notify_user = forms.BooleanField(
        label=_('leaders:forms:create_form:notify_user:label'),
        help_text=_('leaders:forms:create_form:notify_user:help_text:ldap'),
        required=False,  # Bit of a misnomer, it means False is a valid value
        initial=True,
    )

    def clean_email(self):
        """This clean method ensures that we do not create new leaders with
                    existing emails.
                    """
        data = self.cleaned_data['email']

        if not data.endswith('uu.nl'):
            raise forms.ValidationError(
                _('leader:form:email:error:not_uu_mail')
            )

        existing_user = ApiUser.objects.get_by_email(data)

        if existing_user:
            raise forms.ValidationError(
                _('leader:form:email:error:user_exists'))

        return data


class LeaderUpdateForm(forms.Form):
    """This form is meant for updating Leaders

    We're using a regular form, as the info for Leaders are spread over multiple
    models.
    """

    leader = forms.ModelChoiceField(
        Leader.objects.all(),
        widget=forms.HiddenInput
    )

    active = forms.BooleanField(
        label=_('leader:form:active'),
        required=False,
    )

    name = forms.Field(
        label=_('leader:form:name'),
    )

    email = forms.EmailField(
        label=_('leader:form:email'),
    )

    phonenumber = forms.Field(
        label=_('leader:form:phonenumber'),
    )

    keep_current_password = forms.BooleanField(
        label=_('leaders:forms:create_form:keep_current_password:label'),
        help_text=_(
            'leaders:forms:create_form:keep_current_password:help_text'),
        required=False,  # Bit of a misnomer, it means False is a valid value
        initial=True,
    )

    password = forms.Field(
        label=_('leader:form:password'),
        help_text=_('leader:form:password:help_text'),
        required=False,
        widget=forms.PasswordInput,
    )

    confirm_password = forms.Field(
        label=_('leader:form:confirm_password:label'),
        help_text=_('leader:form:confirm_password:help_text'),
        required=False,
        widget=forms.PasswordInput,
    )

    def clean_email(self):
        """This clean method ensures that we do not create new leaders with
                    existing emails.
                    """
        data = self.cleaned_data['email']
        current_leader = self.cleaned_data['leader']

        existing_user = ApiUser.objects.get_by_email(data)

        if existing_user and current_leader != existing_user.leader:
            raise forms.ValidationError(
                _('leader:form:email:error:user_exists'))

        return data

    def clean_confirm_password(self):
        return _clean_confirm_password(self)

    def clean_password(self):
        """Ensures the password fields are not empty if they should be"""
        password = self.cleaned_data['password']

        if not password:
            if not self.cleaned_data['keep_current_password']:
                raise forms.ValidationError(
                    _('leader:form:password:error:empty'))

        return password


class LDAPLeaderUpdateForm(forms.Form):
    """This form is meant for updating Leaders

    We're using a regular form, as the info for Leaders are spread over multiple
    models.
    """

    leader = forms.ModelChoiceField(
        Leader.objects.all(),
        widget=forms.HiddenInput
    )

    active = forms.BooleanField(
        label=_('leader:form:active'),
        required=False,
    )

    name = forms.Field(
        label=_('leader:form:name'),
    )

    email = forms.EmailField(
        label=_('leader:form:email'),
    )

    phonenumber = forms.Field(
        label=_('leader:form:phonenumber'),
    )

    def clean_email(self):
        """This clean method ensures that we do not create new leaders with
                    existing emails.
                    """
        data = self.cleaned_data['email']
        current_leader = self.cleaned_data['leader']

        if not data.endswith('uu.nl'):
            raise forms.ValidationError(
                _('leader:form:email:error:not_uu_mail')
            )

        existing_user = ApiUser.objects.get_by_email(data)

        if existing_user and current_leader != existing_user.leader:
            raise forms.ValidationError(
                _('leader:form:email:error:user_exists'))

        return data
