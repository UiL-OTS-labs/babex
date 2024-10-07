from django.urls import path

from ..views.call_views import (
    AppointmentConfirm,
    AppointmentSendEmail,
    CallHomeView,
    HideCall,
    UpdateCall,
)

urlpatterns = [
    path("<int:experiment>/call/<int:participant>", CallHomeView.as_view(), name="call"),
    path("call/appointment/", AppointmentConfirm.as_view()),
    path("call/appointment/email/<int:pk>/", AppointmentSendEmail.as_view()),
    path("call/appointment/email/", AppointmentSendEmail.as_view()),
    path("call/<int:pk>/", UpdateCall.as_view()),
    path("call/<int:pk>/hide/", HideCall.as_view(), name="call_hide"),
]
