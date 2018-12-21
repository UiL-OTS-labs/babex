import braces.views as braces
from django.views import generic


class HomeView(braces.LoginRequiredMixin, generic.TemplateView):
    template_name = 'main/index.html'
