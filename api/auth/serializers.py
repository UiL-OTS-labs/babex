from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from .authenticators import PostAuthenticator


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
            user = PostAuthenticator.authenticate(request=self.context.get('request'),
                                                  username=username, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('api:auth:login_failed')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('api:auth:missing_values')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
