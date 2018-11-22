from django.views import generic
import braces.views as braces


class HomeView(braces.LoginRequiredMixin, generic.TemplateView):
    template_name = 'main/index.html'
