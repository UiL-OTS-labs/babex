from django.views import generic
from django.urls import reverse_lazy as reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.messages.views import SuccessMessageMixin
import braces.views as braces

from .models import Leader
from .forms import LeaderCreateForm, LeaderUpdateForm
from .utils import create_leader, notify_new_leader, update_leader


class LeaderHomeView(braces.LoginRequiredMixin, generic.ListView):
    template_name = 'leaders/index.html'
    model = Leader


class LeaderCreateView(braces.LoginRequiredMixin, SuccessMessageMixin,
                       generic.FormView):
    template_name = 'leaders/new.html'
    form_class = LeaderCreateForm
    success_url = reverse('leaders:home')
    success_message = _('leaders:create:success_message')

    def form_valid(self, form):
        """This method creates a new leader and if needed, notifies the new user
        of this action.
        """

        data = form.cleaned_data

        leader = create_leader(
            data['name'],
            data['email'],
            data['phonenumber'],
            data['password'],
        )

        if data['notify_user']:
            notify_new_leader(leader)

        return super(LeaderCreateView, self).form_valid(form)


class LeaderUpdateView(braces.LoginRequiredMixin, SuccessMessageMixin,
                       generic.FormView):
    template_name = 'leaders/update.html'
    form_class = LeaderUpdateForm
    success_url = reverse('leaders:home')
    success_message = _('leaders:update:success_message')

    def get_initial(self):
        leader_pk = self.kwargs.pop('pk')
        leader = Leader.objects.get(pk=leader_pk)

        return {
            'name':        leader.name,
            'email':       leader.api_user.email,
            'phonenumber': leader.phonenumber,
            'leader':      leader,
            'active':      leader.api_user.is_active
        }

    def form_valid(self, form):
        data = form.cleaned_data

        # Don't update password without explicit instruction
        if data['keep_current_password']:
            data['password'] = None

        update_leader(
            data['leader'],
            data['name'],
            data['email'],
            data['phonenumber'],
            data['password'],
            data['active'],
        )

        return super(LeaderUpdateView, self).form_valid(form)

# TODO: find out if we need a deleteview, and if that deleteview should actually
#       delete or just deactivate
