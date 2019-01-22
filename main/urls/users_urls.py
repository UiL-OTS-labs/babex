from django.urls import path

from ..views import UserChangePasswordView, UserCreateView, UserDeleteView, \
    UserUpdateView, UsersHomeView

urlpatterns = [
    path('', UsersHomeView.as_view(), name='users_home'),
    path('edit/<int:pk>/', UserUpdateView.as_view(), name='user_edit'),
    path(
        'password/<int:pk>/',
        UserChangePasswordView.as_view(),
        name='user_password'
    ),
    path('delete/<int:pk>/', UserDeleteView.as_view(), name='user_delete'),
    path('create/', UserCreateView.as_view(), name='user_create'),
]
