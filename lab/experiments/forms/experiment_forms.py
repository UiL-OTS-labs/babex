from django import forms
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from cdh.core.forms import TemplatedModelForm, BootstrapCheckboxInput, BootstrapRadioSelect
from cdh.core.mail.widgets import EmailContentEditWidget

from ..models import Experiment


class ExperimentForm(TemplatedModelForm):
    class Meta:
        model = Experiment
        fields = '__all__'
        widgets = {
            'name':         forms.TextInput,
            'duration':     forms.TextInput,
            'compensation': forms.TextInput,
            'use_timeslots': BootstrapRadioSelect(choices=(
                (True, _("experiment:form:use_timeslots:true")),
                (False, _("experiment:form:use_timeslots:false")),
            )),
            'task_description': forms.Textarea({
                'rows': 7,
            }),
            'additional_instructions': forms.Textarea({
                'rows': 7
            }),
            'confirmation_email': EmailContentEditWidget(None),
            'invite_email': EmailContentEditWidget(None),
            'open': BootstrapCheckboxInput,
            'public': BootstrapCheckboxInput,
        }

    def __init__(self, *args, **kwargs):
        super(ExperimentForm, self).__init__(*args, **kwargs)

        self.fields['default_max_places'].widget.attrs.update(
            {
                'min': 1,
            }
        )

        self.fields['confirmation_email'].widget.preview_url = self.preview_url_confirmation()
        self.fields['invite_email'].widget.preview_url = self.preview_url_invite()

        # If we are updating an experiment, make sure you cannot exclude the
        # experiment you are updating!
        if self.instance:
            other_experiments = Experiment.objects.exclude(pk=self.instance.pk)
            self.fields['excluded_experiments'].choices = [
                (x.pk, x.name) for x in other_experiments
            ]

    def preview_url_confirmation(self):
        return reverse('experiments:email_preview', args=('confirmation', self.instance.pk))

    def preview_url_invite(self):
        return reverse('experiments:email_preview', args=('invite', self.instance.pk))
