from rest_framework import serializers

from leaders.models import Leader


class LeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leader
        fields = [
            'email', 'name', 'phonenumber', 'user', 'id'
        ]
        depth = 1

    email = serializers.SerializerMethodField()

    def get_email(self, object):
        return object.user.email
