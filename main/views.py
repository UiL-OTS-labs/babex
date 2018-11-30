from django.views import generic
from django.contrib import messages
import braces.views as braces


class HomeView(braces.LoginRequiredMixin, generic.TemplateView):
    template_name = 'main/index.html'


class RedirectSuccessMessageMixin:
    success_message = ''

    def get(self, *args, **kwargs):
        response = super(RedirectSuccessMessageMixin, self).get(*args, **kwargs)

        messages.success(self.request, self.success_message)

        return response

    def get_success_message(self):
        return self.success_message
