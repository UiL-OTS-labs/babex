from django.contrib import admin
from django.urls import include, path

from .views import SignupDone, SignupView, home

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("cdhcore/", include("cdh.core.urls")),
    # home
    path("", home, name="home"),
    # magiclink
    path("auth/", include("mailauth.urls")),
    # signup
    path("signup/", SignupView.as_view(), name="signup"),
    path("signup/done", SignupDone.as_view(), name="signup.done"),
]
