from django.urls import path

from .views import LeaderCreateView, LeaderHomeView, LeaderUpdateView, \
    LeaderDeleteView, LDAPLeaderCreateView, LDAPLeaderUpdateView

app_name = 'leaders'

urlpatterns = [
    path('', LeaderHomeView.as_view(), name='home'),
    path('new/', LeaderCreateView.as_view(), name='create'),
    path('ldap/new/', LDAPLeaderCreateView.as_view(), name='create_ldap'),
    path('<int:pk>/', LeaderUpdateView.as_view(), name='update'),
    path('ldap/<int:pk>/', LDAPLeaderUpdateView.as_view(), name='update_ldap'),
    path('<int:pk>/delete/', LeaderDeleteView.as_view(), name='delete')
]
