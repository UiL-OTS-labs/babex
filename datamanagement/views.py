import braces.views as braces
from django.urls import reverse_lazy as reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from django.views import generic

from uil.core.views import RedirectActionView
from uil.core.views.mixins import RedirectSuccessMessageMixin

from datamanagement.forms import ThresholdsEditForm
from datamanagement.utils.comments import get_comment_counts
from datamanagement.utils.common import get_thresholds_model
from datamanagement.utils.exp_part_visibility import \
    get_experiments_with_visibility
from datamanagement.utils.invitations import get_invite_counts
from datamanagement.utils.participants import \
    get_participants_with_appointments, get_participants_without_appointments
from experiments.models import Experiment

# TODO: confirmation dialogs, settings, write tests


class OverviewView(braces.LoginRequiredMixin, generic.TemplateView):
    template_name = 'datamanagement/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['invites'] = get_invite_counts()
        context['comments'] = get_comment_counts()
        context['participants'] = get_participants_with_appointments()
        context['participants_no_app'] = get_participants_without_appointments()
        context['participants_num'] = len(context['participants']) + \
                                      len(context['participants_no_app'])
        context['exp_part_visible'] = get_experiments_with_visibility()

        return context


class ThresholdsEditView(braces.LoginRequiredMixin, generic.UpdateView):
    form_class = ThresholdsEditForm
    template_name = 'datamanagement/edit_thresholds.html'
    success_url = reverse('datamanagement:overview')

    def get_object(self, queryset=None):
        return get_thresholds_model()


class DeleteInvitesView(braces.LoginRequiredMixin,
                        RedirectSuccessMessageMixin,
                        RedirectActionView):
    url = reverse('datamanagement:overview')

    def action(self, request):
        pass # TODO: actually delete stuff

    @cached_property
    def experiment(self):
        pk = self.kwargs.get('experiment')

        return Experiment.objects.get(pk=pk)

    def get_success_message(self):
        return _('widgets:messages:deleted_invites').format(
            self.experiment
        )


class DeleteCommentsView(braces.LoginRequiredMixin,
                         RedirectSuccessMessageMixin,
                         RedirectActionView):
    url = reverse('datamanagement:overview')

    def action(self, request):
        pass # TODO: actually delete stuff

    @cached_property
    def experiment(self):
        pk = self.kwargs.get('experiment')

        return Experiment.objects.get(pk=pk)

    def get_success_message(self):
        return _('widgets:messages:deleted_comments').format(
            self.experiment
        )
