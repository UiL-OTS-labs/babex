from rest_framework.authtoken import views
from rest_framework.response import Response

from .serializers import AuthTokenSerializer
from .token import JwtToken
from ..permissions import IsPermittedClient


class ApiLoginView(views.ObtainAuthToken):

    serializer_class = AuthTokenSerializer
    permission_classes = (IsPermittedClient, )

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token = JwtToken.make_token(user)

        groups = [
            {'pk': group.pk, 'name': group.name} for group in user.groups.all()
        ]

        return Response({
            'token': token,
            'is_active': user.is_active,
            'is_admin': user.is_frontend_admin,
            'pk': user.pk,
            'groups': groups,
            'needs_password_change': user.passwords_needs_change,
        })
