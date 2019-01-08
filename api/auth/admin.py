from django.contrib import admin

# Register your models here.
from api.auth.models import ApiUser, ApiGroup

admin.site.register([
    ApiGroup,
    ApiUser,
])
