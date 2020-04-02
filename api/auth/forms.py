from django.contrib.auth.forms import UserCreationForm, UsernameField

from api.auth.models import ApiUser


class ApiUserCreationForm(UserCreationForm):
    class Meta:
        model = ApiUser
        fields = ("email",)
        field_classes = {
            'email': UsernameField
        }