from django.urls import path

from .views import agenda_home, agenda_feed, closing_post, closing_delete

app_name = 'agenda'

urlpatterns = [
    path('', agenda_home, name='home'),
    path('feed', agenda_feed, name='feed'),

    path('closing', closing_post, name='closing.post'),
    path('closing/delete', closing_delete, name='closing.delete'),
]
