from django_auth_ldap.backend import _LDAPUser, logger

from api.auth.models import ApiUser
from main.auth import PpnLdapBackend


class ApiLdapBackend(PpnLdapBackend):
    settings_prefix = "AUTH_LDAP_API_"

    def get_user_model(self):
        return ApiUser

    def authenticate(self, username=None, password=None, **kwargs):
        if password or self.settings.PERMIT_EMPTY_PASSWORD:
            ldap_user = _LDAPUser(self, username=username.strip())
            user = self.authenticate_ldap_user(ldap_user, password)
        else:
            logger.debug('Rejecting empty password for {}'.format(username))
            user = None

        return user

    def _get_user_object(self, model, lookup, query_value):
        try:
            user = model.objects.get(**{
                lookup: query_value
            })
        except model.DoesNotExist:
            # Fix the annoying problem that the university allows student
            # assistants to have 2 emails
            if 'students.uu.nl' in query_value:
                query_value = query_value.replace('students.uu.nl', 'uu.nl')
                user = self._get_user_object(model, lookup, query_value)
            else:
                user = None

        return user