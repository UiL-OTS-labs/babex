from django.urls import path

from .views import SignupDetailView, SignupListView

app_name = 'signups'

urlpatterns = [
    path('', SignupListView.as_view(), name='list'),
    path('<int:pk>/', SignupDetailView.as_view(), name='detail'),
]
