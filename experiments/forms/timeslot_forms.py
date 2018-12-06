from django import forms

from ..models import TimeSlot


class TimeSlotForm(forms.ModelForm):

    class Meta:
        model = TimeSlot
        fields = ['datetime', 'max_places', 'experiment']
        widgets = {
            'experiment': forms.HiddenInput,
        }


