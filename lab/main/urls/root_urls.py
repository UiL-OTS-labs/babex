from cdh.federated_auth.saml.views import LogoutInitView
from django.contrib.auth import views as auth_views
from django.urls import path

from ..views import HomeView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", LogoutInitView.as_view(), name="logout"),
]
