from rest_framework import serializers

from main.models import User


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email'
        ]
