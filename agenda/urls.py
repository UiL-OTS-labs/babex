from django.urls import path

from .views import home

app_name = 'agenda'

urlpatterns = [
    path('', home, name='home')
]
