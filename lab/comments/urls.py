from django.urls import path

from .views import CommentCreateView, CommentsDeleteView

app_name = "comments"

urlpatterns = [
    path("<int:pk>/delete/", CommentsDeleteView.as_view(), name="delete"),
    path(
        "new/",
        CommentCreateView.as_view(),
        name="new",
    ),
]
