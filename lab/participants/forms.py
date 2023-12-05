from cdh.core.forms import BootstrapCheckboxInput, TemplatedModelForm
from django import forms

from .models import CriterionAnswer, Participant
from .widgets import ParticipantSexWidget


class ParticipantForm(TemplatedModelForm):
    class Meta:
        model = Participant
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
            "sex": ParticipantSexWidget,
            "email_subscription": BootstrapCheckboxInput,
            "english_contact": BootstrapCheckboxInput,
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
