from django.conf import settings
from rest_framework.permissions import BasePermission


class IsPermittedClient(BasePermission):

    def has_permission(self, request, view):
        client_ip = request.META.get('REMOTE_ADDR', None)
        client_host = request.META.get('REMOTE_HOST', None)

        if not client_ip or client_ip not in settings.REST_PERMITTED_CLIENTS:
            return False

        if client_host:
            return client_host in settings.REST_PERMITTED_CLIENTS

        return True


class IsLeader(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_leader