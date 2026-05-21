from django.urls import path

from experiments.views import (
    ExperimentArchiveView,
    ExperimentAttachmentView,
    ExperimentCreateView,
    ExperimentCriteriaView,
    ExperimentDeleteView,
    ExperimentDetailView,
    ExperimentHomeView,
    ExperimentUpdateView,
)

urlpatterns = [
    path("", ExperimentHomeView.as_view(), name="home"),
    path("archived/", ExperimentHomeView.as_view(archived=True), name="archived"),
    path("new/", ExperimentCreateView.as_view(), name="create"),
    path("<int:pk>/", ExperimentDetailView.as_view(), name="detail"),
    path("<int:pk>/update/", ExperimentUpdateView.as_view(), name="update"),
    path("<int:pk>/archive/", ExperimentArchiveView.as_view(), name="archive"),
    path("<int:pk>/delete/", ExperimentDeleteView.as_view(), name="delete"),
    path("<int:pk>/attachment/<int:attachment>", ExperimentAttachmentView.as_view(), name="attachment"),
    path("<int:pk>/criteria/", ExperimentCriteriaView.as_view(), name="criteria"),
]
