from django_auth_ldap.backend import LDAPBackend


class PpnLdapBackend(LDAPBackend):

    def get_or_build_user(self, username, ldap_user):
        """
        This must return a (User, built) 2-tuple for the given LDAP user.

        username is the Django-friendly username of the user. ldap_user.dn is
        the user's DN and ldap_user.attrs contains all of their LDAP
        attributes.

        The returned User object may be an unsaved model instance.

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

        try:
            user = model.objects.get(**{
                lookup: query_value
            })
        except model.DoesNotExist:
            user = None

        user.is_ldap_account = True
        user.save()

        return user, False
