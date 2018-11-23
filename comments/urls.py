from django.conf.urls import url
from .views import CommentsHomeView


app_name = 'comments'

urlpatterns = [
    url(r'^$', CommentsHomeView.as_view(), name='home'),
]
