from django.conf import settings
from django.shortcuts import redirect, render

from .base import FormListView, ModelFormListView
from .home import HomeView
from .mixins import RedirectSuccessMessageMixin
from .users import (
    UserChangePasswordView,
    UserCreateView,
    UserDeleteView,
    UserHome,
    UserUpdateView,
)


def error403(request, exception):
    if request.user.is_authenticated:
        return render(request, "403.html", status=403)
    return redirect(settings.LOGIN_URL)


def error404(request, *args, **kwargs):
    return render(request, "error/404.html", status=404)


def error500(request, *args, **kwargs):
    return render(request, "error/500.html", status=500)
