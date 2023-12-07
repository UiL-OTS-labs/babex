from django.urls import path

from experiments.views import DefaultCriteriaUpdateView

urlpatterns = [
    path("default_criteria/", DefaultCriteriaUpdateView.as_view(), name="default_criteria"),
]
