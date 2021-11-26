import braces.views as braces
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import generic

from main.auth import PpnLdapBackend
from main.forms.user_forms import LDAPUserCreationForm, UserUpdateForm
from main.utils import is_ldap_enabled
from ..forms import UserCreationForm
from ..models import User


class UsersHomeView(braces.LoginRequiredMixin, generic.ListView):
    model = User
    template_name = 'users/index.html'

    def get_context_data(self, *args, **kwargs):
        context = super(UsersHomeView, self).get_context_data(
            *args,
            **kwargs
        )

        context['ldap'] = is_ldap_enabled()

        return context


class UserUpdateView(braces.LoginRequiredMixin,
                     SuccessMessageMixin,
                     generic.UpdateView):
    model = User
    template_name = 'users/update.html'
    form_class = UserUpdateForm
    success_url = reverse_lazy('main:users_home')
    success_message = _('users:message:updated')


class LDAPUserUpdateView(braces.LoginRequiredMixin,
                         SuccessMessageMixin,
                         generic.UpdateView):
    model = User
    template_name = 'users/update.html'
    form_class = LDAPUserCreationForm
    success_url = reverse_lazy('main:users_home')
    success_message = _('users:message:updated')


class UserCreateView(braces.LoginRequiredMixin,
                     SuccessMessageMixin,
                     generic.CreateView):
    model = User
    template_name = 'users/create.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('main:users_home')
    success_message = _('users:message:created')


class LDAPUserCreateView(braces.LoginRequiredMixin,
                         SuccessMessageMixin,
                         generic.CreateView):
    model = User
    template_name = 'users/create.html'
    form_class = LDAPUserCreationForm
    success_url = reverse_lazy('main:users_home')
    success_message = _('users:message:created')

    def form_valid(self, form):
        response = super(LDAPUserCreateView, self).form_valid(form)

        PpnLdapBackend().populate_user(self.object.username)

        return response


class UserChangePasswordView(braces.LoginRequiredMixin,
                             SuccessMessageMixin,
                             generic.UpdateView):
    model = User
    template_name = 'users/change_password.html'
    form_class = SetPasswordForm
    success_url = reverse_lazy('main:users_home')
    success_message = _('users:message:changed_password')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # Because this form doesn't follow the rules for some reason, we need to
        # remove the instance kwargs key, and insert the user kwargs key
        if 'instance' in kwargs:
            del kwargs['instance']

        kwargs['user'] = self.get_object()

        return kwargs


class UserDeleteView(braces.LoginRequiredMixin,
                     generic.DeleteView):
    model = User
    template_name = 'users/delete.html'
    success_url = reverse_lazy('main:users_home')
