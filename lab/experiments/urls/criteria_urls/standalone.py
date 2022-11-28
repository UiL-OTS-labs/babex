from django.urls import path

from experiments.views import (CriteriaCreateView,
                               CriteriaDeleteView, CriteriaHomeView,
                               CriteriaUpdateView, )

urlpatterns = [
    path('', CriteriaHomeView.as_view(), name='criteria_home'),
    path('new/', CriteriaCreateView.as_view(), name='criterion_create'),
    path('<int:pk>/', CriteriaUpdateView.as_view(),
         name='criterion_update'),
    path('<int:pk>/delete/', CriteriaDeleteView.as_view(),
         name='criterion_delete'),
]
