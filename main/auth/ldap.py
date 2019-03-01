from django_auth_ldap.backend import LDAPBackend


class PpnLdapBackend(LDAPBackend):

    def get_or_build_user(self, username, ldap_user):
        """
        This override removes the functionality to create new users on login.

        Technically this should be done through a config flag, but that
        doesn't work for some reason.
        """
        model = self.get_user_model()

        if self.settings.USER_QUERY_FIELD:
            query_field = self.settings.USER_QUERY_FIELD
            query_value = \
                ldap_user.attrs[self.settings.USER_ATTR_MAP[query_field]][0]
            lookup = query_field
        else:
            query_field = model.USERNAME_FIELD
            query_value = username.lower()
            lookup = '{}__iexact'.format(query_field)

        print(lookup, query_value)

        user = self._get_user_object(model, lookup, query_value)

        if user:
            user.is_ldap_account = True
            user.save()

        return user, False

    def _get_user_object(self,
                         model,
                         lookup: str,
                         query_value: str):
        try:
            user = model.objects.get(**{
                lookup: query_value
            })
        except model.DoesNotExist:
            user = None

        return user
