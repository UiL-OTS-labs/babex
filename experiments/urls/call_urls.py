from django.urls import path

from ..views.call_views import CallHomeView, AppointmentConfirm, UpdateCall

urlpatterns = [
    path('<int:experiment>/call/<int:participant>', CallHomeView.as_view(), name='call'),


    path('call/appointment/', AppointmentConfirm.as_view()),
    path('call/<int:pk>/', UpdateCall.as_view())
]
