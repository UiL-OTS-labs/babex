from django import forms
from django.utils.text import gettext_lazy as _

from .models import Participant
from .widgets import ParticipantLanguageWidget


class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = [
            'name', 'email', 'language', 'dyslexic', 'birth_date',
            'multilingual', 'phonenumber', 'handedness', 'sex',
            'social_status', 'email_subscription', 'capable'
        ]
        widgets = {
            'name': forms.TextInput,
            'language': ParticipantLanguageWidget,
            'phonenumber': forms.TextInput,
            'handedness': forms.RadioSelect,
            'sex': forms.RadioSelect,
            'social_status': forms.RadioSelect,

        }

    def __init__(self, *args, **kwargs):
        super(ParticipantForm, self).__init__(*args, **kwargs)

        self.fields['multilingual'].widget = forms.RadioSelect(choices=(
            (None, '---------'),
            (True, _("participants:multilingual:many")),
            (False, _("participants:multilingual:one")),
        ))


