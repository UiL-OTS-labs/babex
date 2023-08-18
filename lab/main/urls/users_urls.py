from django.urls import path

from ..views import (
    UserChangePasswordView,
    UserCreateView,
    UserDeleteView,
    UserHome,
    UserUpdateView,
)

urlpatterns = [
    path("", UserHome.as_view(), name="users_leaders"),
    path("edit/<int:pk>/", UserUpdateView.as_view(), name="user_edit"),
    path("password/<int:pk>/", UserChangePasswordView.as_view(), name="user_password"),
    path("delete/<int:pk>/", UserDeleteView.as_view(), name="user_delete"),
    path("create/", UserCreateView.as_view(), name="user_create"),
    path("admins/", UserHome.as_view(is_admins=True), name="users_admins"),
    path("admins/edit/<int:pk>/", UserUpdateView.as_view(is_admins=True), name="admin_edit"),
    path("admins/password/<int:pk>/", UserChangePasswordView.as_view(is_admins=True), name="admin_password"),
    path("admins/delete/<int:pk>/", UserDeleteView.as_view(is_admins=True), name="admin_delete"),
    path("admins/create/", UserCreateView.as_view(is_admins=True), name="admin_create"),
]
