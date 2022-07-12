from django.urls import path

from .views import agenda_home, closing_post, closing_delete

app_name = 'agenda'

urlpatterns = [
    path('', agenda_home, name='home'),

    path('closing', closing_post, name='closing.post'),
    path('closing/delete', closing_delete, name='closing.delete'),
]
