from django import forms

from ..models import Experiment


class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = '__all__'
        widgets = {
            'name':         forms.TextInput,
            'duration':     forms.TextInput,
            'compensation': forms.TextInput,
            'task_description': forms.Textarea({
                'rows': 7,
            }),
            'additional_instructions': forms.Textarea({
                'rows': 7
            })
        }

    def __init__(self, *args, **kwargs):
        super(ExperimentForm, self).__init__(*args, **kwargs)

        self.fields['default_max_places'].widget.attrs.update(
            {
                'min': 1,
                'max': 10,
            }
        )

        # If we are updating an experiment, make sure you cannot exclude the
        # experiment you are updating!
        if self.instance:
            other_experiments = Experiment.objects.exclude(pk=self.instance.pk)
            self.fields['excluded_experiments'].choices = [
                (x.pk, x.name) for x in other_experiments
            ]
