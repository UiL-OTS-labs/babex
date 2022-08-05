from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import gettext_lazy as _

from .models import CriterionAnswer, Participant
from .widgets import ParticipantLanguageWidget, ParticipantSexWidget


class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = [
            'name', 'email', 'language', 'dyslexic_parent', 'birth_date',
            'multilingual', 'phonenumber', 'sex',
            'email_subscription', 'capable'
        ]
        widgets = {
            'name': forms.TextInput,
            'language': ParticipantLanguageWidget,
            'phonenumber': forms.TextInput,
            'sex': ParticipantSexWidget,

        }

    def __init__(self, *args, **kwargs):
        super(ParticipantForm, self).__init__(*args, **kwargs)

        self.fields['multilingual'].widget = forms.RadioSelect(choices=(
            (None, '---------'),
            (True, _("participants:multilingual:many")),
            (False, _("participants:multilingual:one")),
        ))


class CriterionAnswerForm(forms.ModelForm):
    class Meta:
        model = CriterionAnswer
        fields = ['answer']
        widgets = {
            'answer': forms.RadioSelect
        }

    def __init__(self, *args, **kwargs):
        super(CriterionAnswerForm, self).__init__(*args, **kwargs)

        self.fields['answer'].label = self.instance.criterion.name_natural
        self.fields['answer'].widget.choices = \
            self.instance.criterion.choices_tuple
