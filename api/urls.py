from django.urls import include, path

import api.auth.views as auth_views
from .router import router
from .views import AdminView

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', AdminView.as_view()),
    path('api-auth/', include('rest_framework.urls',
                              namespace='rest_framework')),
    path('auth/', auth_views.ApiLoginView.as_view())
]
