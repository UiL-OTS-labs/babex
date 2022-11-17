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

    def post(self, request, format=None):
        if not hasattr(self.request.user, 'leader'):
            raise PermissionDenied

        post_data = self.request.POST
        leader = self.request.user.leader

        try:
            # We want to compare int's, but we have a string in the POST data
            post_id = int(post_data['id'])
        except ValueError:
            raise PermissionDenied

        if not leader.id == post_id:
            raise PermissionDenied

        leader.name = post_data['name']
        leader.phonenumber = post_data['phonenumber']
        leader.save()

        serializer = self.serializer_class(leader)

        return Response(serializer.data)
