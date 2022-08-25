from django_auth_ldap.backend import _LDAPUser, logger

from api.auth.models import ApiUser
from main.auth import PpnLdapBackend


class ApiLdapBackend(PpnLdapBackend):
    settings_prefix = "AUTH_LDAP_API_"

    def get_user_model(self):
        return ApiUser

    def authenticate(self, username=None, password=None, **kwargs):
        if username is None:
            logger.debug('Rejecting empty password for {}'.format(username))
            return None

        if password or self.settings.PERMIT_EMPTY_PASSWORD:
            ldap_user = _LDAPUser(self, username=username.strip())
            user = self.authenticate_ldap_user(ldap_user, password)
        else:
            logger.debug('Rejecting empty password for {}'.format(username))
            user = None

        return user

    def _get_user_object(self,
                         model,
                         lookup: str,
                         query_value: str):
        try:
            user = model.objects.get_by_email(**{
                lookup: query_value
            })
        except model.DoesNotExist:
            user = None

        return user
