from django.core.exceptions import ValidationError
from rest_framework import views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.auth.authenticators import JwtAuthentication
from api.auth.models import ApiUser, UserToken
from api.permissions import IsPermittedClient
from api.utils.create_participant_account import \
    ReturnValues as CPAReturnValues, create_participant_account
from ..utils import send_password_reset_mail


class ChangePasswordView(views.APIView):
    permission_classes = (IsPermittedClient, IsAuthenticated)
    authentication_classes = (JwtAuthentication,)

    def post(self, request):
        user = request.user

        post_data = self.request.POST

        success = False

        if not user.is_ldap_account and \
                user.check_password(
                    post_data['current_password']
                ):
            user.set_password(post_data['new_password'])
            user.passwords_needs_change = False
            user.save()

            success = True

        return Response({
            'success': success
        })


class ForgotPasswordView(views.APIView):
    permission_classes = (IsPermittedClient,)

    def post(self, request):

        email = request.POST.get('email', None)

        success = False
        ldap_blocked = False

        if email:
            try:
                user = ApiUser.objects.get_by_email(email)

                if not user:
                    raise ApiUser.DoesNotExist

                if user.is_ldap_account:
                    # Slightly hacky, but this way we don't enter a new ident
                    # level. And we could justify this as 'the password does
                    # not exist'
                    ldap_blocked = True
                    raise ApiUser.DoesNotExist

                token = UserToken.objects.create(
                    user=user,
                    type=UserToken.PASSWORD_RESET,
                )

                send_password_reset_mail(user, str(token.token))

                success = True
            except ApiUser.DoesNotExist:
                pass

        return Response({
            'success':      success,
            'ldap_blocked': ldap_blocked,
        })


class ValidateTokenView(views.APIView):
    permission_classes = (IsPermittedClient,)

    def post(self, request):

        token = request.POST.get('token', None)

        success = False

        if token:
            try:
                o = UserToken.objects.get(
                    token=token,
                    type=UserToken.PASSWORD_RESET,
                )

                success = o.is_valid()

                # If it's not a valid token, delete the token from the DB
                if not success:
                    o.delete()

            except (ValidationError, UserToken.DoesNotExist):
                pass

        return Response({
            'success': success
        })


class ResetPasswordView(views.APIView):
    permission_classes = (IsPermittedClient,)

    def post(self, request):

        token = request.POST.get('token', None)
        new_password = request.POST.get('new_password', None)
        success = False

        if token and new_password:
            try:
                o = UserToken.objects.select_related('user').get(
                    token=token,
                    type=UserToken.PASSWORD_RESET,
                )

                if o.is_valid():
                    user = o.user

                    if user.is_ldap_account:
                        # Slightly hacky, but this way we don't enter a new
                        # ident level. And we could justify this as 'the
                        # password does not exist'
                        raise ApiUser.DoesNotExist

                    user.set_password(new_password)
                    user.passwords_needs_change = False
                    user.save()

                    o.delete()

                    success = True

            except UserToken.DoesNotExist:
                pass

        return Response({
            'success': success
        })
