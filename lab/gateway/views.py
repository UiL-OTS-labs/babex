from rest_framework import views
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.response import Response

from signups.models import Signup
from signups.serializers import SignupSerializer


class GatewayHome(views.APIView):
    def get(self, request, *args, **kwargs):
        return Response(dict())


class Signups(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = Signup.objects.all()
    serializer_class = SignupSerializer
