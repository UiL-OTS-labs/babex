from django.urls import path

from ..views import LDAPUserCreateView, LDAPUserUpdateView, \
    UserChangePasswordView,  UserCreateView, UserDeleteView, UserUpdateView, \
    UserHome

urlpatterns = [
    path('', UserHome.as_view(), name='users_leaders'),
    path('edit/<int:pk>/', UserUpdateView.as_view(), name='user_edit'),
    path('ldap/edit/<int:pk>/', LDAPUserUpdateView.as_view(), name='user_edit_ldap'),
    path('password/<int:pk>/', UserChangePasswordView.as_view(), name='user_password'),
    path('delete/<int:pk>/', UserDeleteView.as_view(), name='user_delete'),
    path('create/', UserCreateView.as_view(), name='user_create'),
    path('ldap/create/', LDAPUserCreateView.as_view(), name='user_create_ldap'),

    path('admins/', UserHome.as_view(is_admins=True), name='users_admins'),
    path('admins/edit/<int:pk>/', UserUpdateView.as_view(is_admins=True), name='admin_edit'),
    path('admins/ldap/edit/<int:pk>/', LDAPUserUpdateView.as_view(is_admins=True), name='admin_edit_ldap'),
    path('admins/password/<int:pk>/', UserChangePasswordView.as_view(is_admins=True), name='admin_password'),
    path('admins/delete/<int:pk>/', UserDeleteView.as_view(is_admins=True), name='admin_delete'),
    path('admins/create/', UserCreateView.as_view(is_admins=True), name='admin_create'),
    path('admins/ldap/create/', LDAPUserCreateView.as_view(is_admins=True), name='admin_create_ldap'),
]
