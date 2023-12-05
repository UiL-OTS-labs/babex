from cdh.core.forms import (
    BootstrapCheckboxInput,
    BootstrapRadioSelect,
    TemplatedModelForm,
)
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import CriterionAnswer, ExtraData, Participant
from .widgets import ParticipantSexWidget


class ParticipantForm(TemplatedModelForm):
    class Meta:
        model = Participant
        fields = [
            "name",
            "email",
            "dyslexic_parent",
            "birth_date",
            "languages",
            "phonenumber",
            "sex",
            "email_subscription",
        ]
        widgets = {
            "name": forms.TextInput,
            "phonenumber": forms.TextInput,
            "sex": ParticipantSexWidget,
            "email_subscription": BootstrapCheckboxInput,
        }

    def __init__(self, *args, **kwargs):
        super(ParticipantForm, self).__init__(*args, **kwargs)


class CriterionAnswerForm(forms.ModelForm):
    class Meta:
        model = CriterionAnswer
        fields = ["answer"]
        widgets = {"answer": forms.RadioSelect}

    def __init__(self, *args, **kwargs):
        super(CriterionAnswerForm, self).__init__(*args, **kwargs)

        self.fields["answer"].label = self.instance.criterion.name_natural
        self.fields["answer"].widget.choices = self.instance.criterion.choices_tuple


class ExtraDataForm(TemplatedModelForm):
    class Meta:
        model = ExtraData
        fields = ["title", "content"]