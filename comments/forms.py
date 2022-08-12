from django import forms

from experiments.models import Experiment
from participants.models import Participant
from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['participant', 'comment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['participant'].widget = forms.HiddenInput()
