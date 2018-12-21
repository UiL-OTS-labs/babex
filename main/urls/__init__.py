from django.urls import include, path

app_name = 'main'

urlpatterns = [
    path('', include('main.urls.root_urls')),

    path('admins/', include('main.urls.admins_urls'))
]
