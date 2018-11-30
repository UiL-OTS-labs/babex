from django.conf.urls import url
from .views import CommentsHomeView, CommentsDeleteView


app_name = 'comments'

urlpatterns = [
    url(r'^$', CommentsHomeView.as_view(), name='home'),
    url(r'(?P<pk>\d+)/delete/', CommentsDeleteView.as_view(), name='delete')
]
