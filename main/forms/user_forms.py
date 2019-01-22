import django.contrib.auth.forms as auth_forms

from main.models import User


class UserCreationForm(auth_forms.UserCreationForm):
    class Meta:
        fields = ('username', 'first_name', 'last_name')
        model = User
        field_classes = {
            'username': auth_forms.UsernameField
        }
