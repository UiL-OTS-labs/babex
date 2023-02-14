from rest_framework import serializers

from .models import Signup


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signup
        fields = ['name', 'sex', 'birth_date',

                  'parent_name', 'city', 'phonenumber', 'phonenumber_alt',
                  'email',

                  'english_contact', 'newsletter',

                  'dyslexic_parent', 'tos_parent', 'speech_parent', 'multilingual'
                  ]
