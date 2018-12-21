from django.urls import path

from .views import LeaderCreateView, LeaderHomeView, LeaderUpdateView, LeaderDeleteView

app_name = 'leaders'

urlpatterns = [
    path('', LeaderHomeView.as_view(), name='home'),
    path('new/', LeaderCreateView.as_view(), name='create'),
    path('<int:pk>/', LeaderUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', LeaderDeleteView.as_view(), name='delete')
]
