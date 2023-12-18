from cdh.core.forms import (
    BootstrapCheckboxInput,
    BootstrapRadioSelect,
    TemplatedModelForm,
)
from django import forms

from .models import ExtraData, ParticipantData


class ParticipantForm(TemplatedModelForm):
    class Meta:
        model = ParticipantData
        # note: this form intentionally does not include the more sensitive fields,
        # because it's also less likely that an experiment leader would have to edit those
        fields = [
            "name",
            "email",
            "birth_date",
            "languages",
            "phonenumber",
            "phonenumber_alt",
            "sex",
            "email_subscription",
            "english_contact",
        ]
        widgets = {
            "name": forms.TextInput,
            "phonenumber": forms.TextInput,
            "phonenumber_alt": forms.TextInput,
            "sex": BootstrapRadioSelect,
            "email_subscription": BootstrapCheckboxInput,
            "english_contact": BootstrapCheckboxInput,
        }

    def __init__(self, *args, **kwargs):
        super(ParticipantForm, self).__init__(*args, **kwargs)


class ExtraDataForm(TemplatedModelForm):
    class Meta:
        model = ExtraData
        fields = ["title", "content"]
