from django.urls import path

from ..views import UsersHomeView

urlpatterns = [
    path('', UsersHomeView.as_view(), name='users_home'),
]
