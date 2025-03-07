from cdh.core.forms import BootstrapCheckboxInput, TemplatedModelForm
from cdh.mail.widgets import EmailContentEditWidget
from django import forms
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ..models.experiment_models import ConfirmationMailAttachment, Experiment


class MultiUploadWidget(forms.Widget):
    template_name = "experiments/forms/multi_upload.html"
    needs_multipart_form = True
    nonce = ""

    def get_context(self, *args, **kwargs):
        return dict(nonce=self.nonce, **super().get_context(*args, **kwargs))

    def format_value(self, value):
        return value


class MultiUploadField(forms.Field):
    widget = MultiUploadWidget


class ExperimentForm(TemplatedModelForm):
    attachments = MultiUploadField(required=False, label=_("experiments:forms:attachments"))
    show_valid_fields = False

    class Meta:
        model = Experiment
        fields = [
            "name",
            "duration",
            "session_duration",
            "recruitment_target",
            "task_description",
            "location",
            "confirmation_email",
            "attachments",
            "reminder_email",
            "send_reminders",
            "excluded_experiments",
            "required_experiments",
            "leaders",
            "responsible_researcher",
        ]

        exclude = ("defaultcriteria",)
        widgets = {
            "name": forms.TextInput,
            "task_description": forms.Textarea(
                {
                    "rows": 7,
                }
            ),
            "confirmation_email": EmailContentEditWidget(None),
            "reminder_email": EmailContentEditWidget(None),
            "send_reminders": BootstrapCheckboxInput,
            "responsible_researcher": forms.TextInput,
        }

    def __init__(self, *args, csp_nonce="", **kwargs):
        super(ExperimentForm, self).__init__(*args, **kwargs)

        self.fields["confirmation_email"].widget.preview_url = self.preview_url_confirmation()
        self.fields["reminder_email"].widget.preview_url = self.preview_url_reminder()

        if self.instance.pk:
            self.fields["attachments"].initial = [
                {"pk": f.pk, "name": f.filename, "created": f.created, "link": f.link}
                for f in self.instance.attachments.all()
            ]
        self.fields["attachments"].widget.nonce = csp_nonce

        # If we are updating an experiment, make sure you cannot exclude or require the
        # experiment you are updating!
        if self.instance:
            other_experiments = Experiment.objects.exclude(pk=self.instance.pk)
            self.fields["excluded_experiments"].choices = [(x.pk, x.name) for x in other_experiments]
            self.fields["required_experiments"].choices = [(x.pk, x.name) for x in other_experiments]

    def preview_url_confirmation(self):
        if self.instance.pk is not None:
            return reverse("experiments:email_preview", args=("confirmation", self.instance.pk))
        return reverse("experiments:email_preview", args=("confirmation",))

    def preview_url_reminder(self):
        if self.instance.pk is not None:
            return reverse("experiments:email_preview", args=("reminder", self.instance.pk))
        return reverse("experiments:email_preview", args=("reminder",))

    def save(self, *args, **kwargs):
        experiment = super().save(*args, **kwargs)

        for entry in self.files.getlist("attachments"):
            ConfirmationMailAttachment.objects.create(experiment=experiment, file=entry, filename=entry.name)

        for entry in self.data.getlist("attachments_remove"):
            experiment.attachments.filter(pk=entry).delete()

        return experiment
