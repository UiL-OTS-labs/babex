from rest_framework import views
from rest_framework.response import Response

from api.permissions import IsPermittedClient
from api.serializers.admin_serializers import AdminSerializer
from main.models import User


class AdminView(views.APIView):
    serializer_class = AdminSerializer
    permission_classes = (IsPermittedClient,)

    def get(self, request, format=None):
        users = User.objects.filter(is_supreme_admin=True)

        serializer = self.serializer_class(users[0])

        return Response(serializer.data)
