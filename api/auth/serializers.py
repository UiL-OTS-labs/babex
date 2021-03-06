from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .authenticators import PostAuthenticator
from .models import ApiUser


class ApiUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiUser
        fields = [
            'email', 'date_joined', 'groups', 'id', 'is_active',
            'is_frontend_admin', 'last_login', 'passwords_needs_change'
        ]


class AuthTokenSerializer(serializers.Serializer):

    def update(self, instance, validated_data):
        raise NotImplementedError

    def create(self, validated_data):
        raise NotImplementedError

    username = serializers.CharField(label=_("Username"))
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = PostAuthenticator.authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('api:auth:login_failed')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('api:auth:missing_values')
            raise serializers.ValidationError(msg, code='authorization')

        user.last_login = timezone.now()
        attrs['user'] = user
        return attrs
