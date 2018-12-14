from django import forms

from .models import Comment
from experiments.models import Experiment
from participants.models import Participant


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['participant', 'experiment', 'comment']

    def __init__(self, *args, **kwargs):
        """
        This override handles limiting the options for the participant and
        experiment values to 1, namely those supplied in the initial dataset.

        The original intention was to set the fields to disabled,
        but disabled fields are not sent along. This caused Django to raise
        ValidationErrors because the fields were 'empty'.

        If it's stupid but it works....
        """
        super().__init__(*args, **kwargs)

        self.fields['experiment'].queryset = Experiment.objects.filter(
            pk=self.initial['experiment'])
        self.fields['experiment'].empty_label = None

        self.fields['participant'].queryset = Participant.objects.filter(
            pk=self.initial['participant'])
        self.fields['participant'].empty_label = None

