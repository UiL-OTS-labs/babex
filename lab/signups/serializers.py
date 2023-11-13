from rest_framework import serializers

from .models import Signup


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signup
        fields = [
            "name",
            "sex",
            "birth_date",
            "birth_weight",
            "pregnancy_duration",
            "parent_first_name",
            "parent_last_name",
            "phonenumber",
            "phonenumber_alt",
            "email",
            "english_contact",
            "newsletter",
            "dyslexic_parent",
            "tos_parent",
            "languages",
        ]
