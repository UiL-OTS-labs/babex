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
            "pregnancy_weeks",
            "pregnancy_days",
            "parent_name",
            "phonenumber",
            "phonenumber_alt",
            "email",
            "english_contact",
            "newsletter",
            "dyslexic_parent",
            "multilingual",
        ]
