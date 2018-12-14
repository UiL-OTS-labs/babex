from django.conf.urls import url

from .views import CommentCreateView, CommentsDeleteView, CommentsHomeView

app_name = 'comments'

urlpatterns = [
    url(r'^$', CommentsHomeView.as_view(), name='home'),
    url(r'^(?P<pk>\d+)/delete/$', CommentsDeleteView.as_view(), name='delete'),
    url(
        r'^new/(?P<participant>\d+)/(?P<experiment>\d+)/$',
        CommentCreateView.as_view(),
        name='new',
    ),
]
