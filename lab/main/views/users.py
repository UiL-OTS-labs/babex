import braces.views as braces
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import generic

from main.auth import PpnLdapBackend
from main.forms.user_forms import LDAPUserCreationForm, UserUpdateForm
from main.utils import is_ldap_enabled
from ..forms import UserCreationForm
from ..models import User


class BaseUserView(UserPassesTestMixin):
    is_admins = False  # to be overriden in as_view()

    def test_func(self):
        if hasattr(self, 'object'):
            # views that mutate a user

            if self.object.is_staff:
                # only superusers can manage staff users
                return self.request.user.is_superuser
            # but every staff user can manage leaders
            return self.request.is_staff
        else:
            # list view
            if self.is_admins:
                return self.request.user.is_superuser
            return self.request.user.is_staff

    def get_success_url(self):
        if self.is_admins:
            return reverse_lazy('main:users_admins')
        return reverse_lazy('main:users_leaders')

    def get_queryset(self):
        if self.is_admins:
            return User.objects.filter(is_staff=True)
        return User.objects.exclude(is_staff=True)

    def get_context_data(self):
        context = super().get_context_data()
        context['is_admins'] = self.is_admins
        return context


class UserHome(BaseUserView, generic.ListView):
    template_name = 'users/index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['ldap'] = is_ldap_enabled()
        return context


class UserUpdateView(BaseUserView, SuccessMessageMixin, generic.UpdateView):
    template_name = 'users/update.html'
    form_class = UserUpdateForm
    success_message = _('users:message:updated')


class LDAPUserUpdateView(BaseUserView, SuccessMessageMixin, generic.UpdateView):
    template_name = 'users/update.html'
    form_class = LDAPUserCreationForm
    success_message = _('users:message:updated')


class UserCreateView(BaseUserView, SuccessMessageMixin, generic.CreateView):
    template_name = 'users/create.html'
    form_class = UserCreationForm
    success_message = _('users:message:created')


class LDAPUserCreateView(BaseUserView, SuccessMessageMixin, generic.CreateView):
    template_name = 'users/create.html'
    form_class = LDAPUserCreationForm
    success_message = _('users:message:created')

    def form_valid(self, form):
        response = super().form_valid(form)
        PpnLdapBackend().populate_user(self.object.username)
        return response


class UserChangePasswordView(BaseUserView, SuccessMessageMixin, generic.UpdateView):
    template_name = 'users/change_password.html'
    form_class = SetPasswordForm
    success_message = _('users:message:changed_password')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # Because this form doesn't follow the rules for some reason, we need to
        # remove the instance kwargs key, and insert the user kwargs key
        if 'instance' in kwargs:
            del kwargs['instance']

        kwargs['user'] = self.get_object()

        return kwargs


class UserDeleteView(BaseUserView, generic.DeleteView):
    template_name = 'users/delete.html'
