from django.urls import path

from .views import CommentCreateView, CommentsDeleteView, CommentsHomeView

app_name = 'comments'

urlpatterns = [
    path('', CommentsHomeView.as_view(), name='home'),
    path('<int:pk>/delete/', CommentsDeleteView.as_view(), name='delete'),
    path(
        'new/',
        CommentCreateView.as_view(),
        name='new',
    ),
]
