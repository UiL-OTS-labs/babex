from django.urls import path

from .views import AgendaHomeView

app_name = 'agenda'

urlpatterns = [
    path('', AgendaHomeView.as_view(), name='home')
]
