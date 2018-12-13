from django.views import generic
from django.urls import reverse_lazy as reverse
import braces.views as braces

from .models import Comment


class CommentsHomeView(braces.LoginRequiredMixin, generic.ListView):
    template_name = 'comments/index.html'
    model = Comment

    def get_queryset(self):
        """Return a queryset that's been instructed to also pull the related
        objects. This makes this page around 10 times faster"""
        return self.model.objects.select_related('participant', 'leader',
                                                 'experiment')


class CommentsDeleteView(braces.LoginRequiredMixin, generic.DeleteView):
    model = Comment
    success_url = reverse('comments:home')
    template_name = 'comments/delete.html'
