from django.views import generic
import braces.views as braces

from .models import Comment


class CommentsHomeView(braces.LoginRequiredMixin, generic.ListView):
    template_name = 'comments/index.html'
    model = Comment
