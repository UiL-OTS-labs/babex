from rest_framework import serializers

from leaders.models import Leader


class LeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leader
        fields = [
            'email', 'name', 'phonenumber', 'api_user', 'id'
        ]
        depth = 1

    email = serializers.SerializerMethodField()

    def get_email(self, object):
        return object.api_user.email
