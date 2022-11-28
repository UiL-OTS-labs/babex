from django.urls import path

from ..views import (LocationCreateView,
                     LocationHomeView, UpdateLocationView,
                     )

urlpatterns = [
    path('', LocationHomeView.as_view(), name='location_home'),
    path('new/', LocationCreateView.as_view(), name='location_create'),
    path('<int:pk>/', UpdateLocationView.as_view(),
         name='location_update')
]
