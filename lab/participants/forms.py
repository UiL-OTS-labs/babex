from cdh.core.forms import BootstrapCheckboxInput, TemplatedModelForm
from django import forms

from .models import ExtraData, ParticipantData


class ParticipantForm(TemplatedModelForm):
    show_valid_fields = False

    class Meta:
        model = ParticipantData
        exclude = []
        widgets = {
            "name": forms.TextInput,
            "phonenumber": forms.TextInput,
            "phonenumber_alt": forms.TextInput,
            "parent_first_name": forms.TextInput,
            "parent_last_name": forms.TextInput,
            "save_longer": BootstrapCheckboxInput,
            "email_subscription": BootstrapCheckboxInput,
            "english_contact": BootstrapCheckboxInput,
        }


class LeaderParticipantForm(TemplatedModelForm):
    show_valid_fields = False

    class Meta:
        model = ParticipantData
        # note: this form intentionally does not include the more sensitive fields,
        # because it's also less likely that an experiment leader would have to edit those
        exclude = ["pregnancy_duration", "birth_weight", "dyslexic_parent", "tos_parent", "save_longer"]
        widgets = {
            "name": forms.TextInput,
            "phonenumber": forms.TextInput,
            "phonenumber_alt": forms.TextInput,
            "parent_first_name": forms.TextInput,
            "parent_last_name": forms.TextInput,
            "save_longer": BootstrapCheckboxInput,
            "email_subscription": BootstrapCheckboxInput,
            "english_contact": BootstrapCheckboxInput,
        }


class ExtraDataForm(TemplatedModelForm):
    show_valid_fields = False

    class Meta:
        model = ExtraData
        fields = ["title", "content"]
