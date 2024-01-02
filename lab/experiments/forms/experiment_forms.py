from cdh.core.forms import (
    BootstrapCheckboxInput,
    BootstrapRadioSelect,
    TemplatedModelForm,
)
from cdh.core.mail.widgets import EmailContentEditWidget
from django import forms
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ..models import Experiment


class ExperimentForm(TemplatedModelForm):
    class Meta:
        model = Experiment
        fields = "__all__"
        exclude = ("defaultcriteria",)
        widgets = {
            "name": forms.TextInput,
            "duration": forms.TextInput,
            "task_description": forms.Textarea(
                {
                    "rows": 7,
                }
            ),
            "additional_instructions": forms.Textarea({"rows": 7}),
            "confirmation_email": EmailContentEditWidget(None),
            "invite_email": EmailContentEditWidget(None),
            "open": BootstrapCheckboxInput,
        }

    def __init__(self, *args, **kwargs):
        super(ExperimentForm, self).__init__(*args, **kwargs)

        self.fields["confirmation_email"].widget.preview_url = self.preview_url_confirmation()
        self.fields["invite_email"].widget.preview_url = self.preview_url_invite()

        # If we are updating an experiment, make sure you cannot exclude the
        # experiment you are updating!
        if self.instance:
            other_experiments = Experiment.objects.exclude(pk=self.instance.pk)
            self.fields["excluded_experiments"].choices = [(x.pk, x.name) for x in other_experiments]

    def preview_url_confirmation(self):
        if self.instance.pk is not None:
            return reverse("experiments:email_preview", args=("confirmation", self.instance.pk))
        # TODO: how to preview with unsaved experiment?

    def preview_url_invite(self):
        if self.instance.pk is not None:
            return reverse("experiments:email_preview", args=("invite", self.instance.pk))
        # TODO
