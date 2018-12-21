import braces.views as braces
from django.views import generic

from ..models import User


class UsersHomeView(braces.LoginRequiredMixin, generic.ListView):
    model = User
    template_name = 'users/index.html'
