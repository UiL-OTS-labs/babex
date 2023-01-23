from django.urls import include, path

app_name = 'main'

urlpatterns = [
    path('', include('main.urls.root_urls')),

    path('users/', include('main.urls.users_urls')),

    path('gateway/', include('gateway.urls')),
]
