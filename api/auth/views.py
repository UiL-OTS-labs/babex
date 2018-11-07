from rest_framework.authtoken import views
from rest_framework.response import Response

from .token import JwtToken
from .serializers import AuthTokenSerializer


class ApiLoginView(views.ObtainAuthToken):

    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token = JwtToken.make_token(user)
        return Response({
            'token': token,
            'is_active': user.is_active,
            'is_admin': user.is_frontend_admin,
            'pk': user.pk,
        })
