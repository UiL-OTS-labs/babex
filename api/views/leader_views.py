from django.core.exceptions import PermissionDenied
from rest_framework import views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.auth.authenticators import JwtAuthentication
from api.permissions import IsPermittedClient
from api.serializers.leader_serializers import LeaderSerializer


class LeaderView(views.APIView):
    serializer_class = LeaderSerializer
    permission_classes = (IsPermittedClient, IsAuthenticated, )
    authentication_classes = (JwtAuthentication, )

    def get(self, request, format=None):
        if not hasattr(self.request.user, 'leader'):
            raise PermissionDenied

        leader = self.request.user.leader
        serializer = self.serializer_class(leader)

        return Response(serializer.data)


class ChangeLeaderView(views.APIView):
    serializer_class = LeaderSerializer
    permission_classes = (IsPermittedClient, )
    authentication_classes = (JwtAuthentication, )

    def post(self, request, format=None):
        if not hasattr(self.request.user, 'leader'):
            raise PermissionDenied

        post_data = self.request.POST
        leader = self.request.user.leader

        leader.name = post_data['name']
        leader.phonenumber = post_data['phonenumber']
        leader.save()

        serializer = self.serializer_class(leader)

        return Response(serializer.data)
