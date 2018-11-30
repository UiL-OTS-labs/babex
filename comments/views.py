from django.views import generic
from django.urls import reverse_lazy as reverse
import braces.views as braces

from .models import Comment


class CommentsHomeView(braces.LoginRequiredMixin, generic.ListView):
    template_name = 'comments/index.html'
    model = Comment


class CommentsDeleteView(braces.LoginRequiredMixin, generic.DeleteView):
    model = Comment
    success_url = reverse('comments:home')
    template_name = 'comments/delete.html'
