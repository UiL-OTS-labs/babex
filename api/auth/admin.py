from django.contrib import admin, messages
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import unquote
from django.contrib.auth import admin as auth_admin, update_session_auth_hash
from django.contrib.auth.admin import sensitive_post_parameters_m
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import escape
from django.utils.translation import gettext, gettext_lazy as _

# Register your models here.
from api.auth.forms import ApiUserCreationForm
from api.auth.models import ApiGroup, ApiUser


@admin.register(ApiGroup)
class ApiGroupAdmin(auth_admin.GroupAdmin):
    filter_horizontal = ()


@admin.register(ApiUser)
class ApiUserAdmin(auth_admin.UserAdmin):
    fieldsets = (
        (None, {
            'fields': ('password', )
        }),
        (_('Personal info'), {
            'fields': ('email',)
        }),
        ('Linked profiles', {
            'fields': ('participant', 'leader',)
        }),
        (_('Permissions'), {
            'fields': ('is_frontend_admin', 'groups',)
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields':  ('email', 'password1', 'password2'),
        }),
    )
    filter_horizontal = ('groups',)
    ordering = ('email',)
    add_form = ApiUserCreationForm
    list_display = ('email', 'is_frontend_admin')
    list_filter = ('is_frontend_admin', 'is_active', 'groups')
    search_fields = ('email', )
    readonly_fields = ["date_joined", "participant", "leader"]

    @sensitive_post_parameters_m
    def user_change_password(self, request, id, form_url=''):
        if not self.has_change_permission(request):
            raise PermissionDenied
        user = self.get_object(request, unquote(id))
        if user is None:
            raise Http404(_(
                '%(name)s object with primary key %(key)r does not exist.') % {
                              'name': self.model._meta.verbose_name,
                              'key':  escape(id),
                          })
        if request.method == 'POST':
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(request, form,
                                                               None)
                self.log_change(request, user, change_message)
                msg = gettext('Password changed successfully.')
                messages.success(request, msg)
                update_session_auth_hash(request, form.user)
                return HttpResponseRedirect(
                    reverse(
                        '%s:%s_%s_change' % (
                            self.admin_site.name,
                            user._meta.app_label,
                            user._meta.model_name,
                        ),
                        args=(user.pk,),
                    )
                )
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {
            'fields': list(form.base_fields)
        })]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title':                 _('Change password: %s') % escape(
                user.email),
            'adminForm':             adminForm,
            'form_url':              form_url,
            'form':                  form,
            'is_popup':              (IS_POPUP_VAR in request.POST or
                                      IS_POPUP_VAR in request.GET),
            'add':                   True,
            'change':                False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url':      False,
            'opts':                  self.model._meta,
            'original':              user,
            'save_as':               False,
            'show_save':             True,
        }
        context.update(self.admin_site.each_context(request))

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request,
            self.change_user_password_template or
            'admin/auth/user/change_password.html',
            context,
        )
