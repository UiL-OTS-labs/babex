from rest_framework import serializers

from api.auth.serializers import ApiUserSerializer
from leaders.models import Leader


class LeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leader
        fields = [
            'email', 'name', 'phonenumber', 'api_user', 'id'
        ]
        depth = 1

    email = serializers.SerializerMethodField()

    api_user = serializers.SerializerMethodField()

    def get_email(self, object):
        return object.api_user.email

    def get_api_user(self, object):
        return ApiUserSerializer(object.api_user).data
