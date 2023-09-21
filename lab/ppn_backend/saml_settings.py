from os import path

from cdh.federated_auth.saml.settings import (
    SAML_APPS,
    SAML_MIDDLEWARE,
    create_saml_config,
)
from django.urls import reverse_lazy


def enable_saml(namespace):
    base_dir = path.dirname(path.dirname(__file__))

    namespace["SAML_CONFIG"] = create_saml_config(
        base_url="http://localhost:8000",
        name="babex",
        key_file=path.join(base_dir, "certs/private.key"),
        cert_file=path.join(base_dir, "certs/public.cert"),
        # idp_metadata="https://login.uu.nl/nidp/saml2/metadata",
        idp_metadata="http://localhost:7000/saml/idp/metadata/",
        contact_given_name="Ben",
        contact_email="ben@localhost.local",
    )

    namespace["SAML_ATTRIBUTE_MAPPING"] = {
        "uushortid": ("username",),
        "mail": ("email",),
        "givenName": ("name",),
        "uuPrefixedSn": ("phonenumber",),
    }

    namespace["AUTHENTICATION_BACKENDS"] = (
        "django.contrib.auth.backends.ModelBackend",
        "djangosaml2.backends.Saml2Backend",
    )

    namespace["LOGIN_URL"] = reverse_lazy("saml2_login")

    namespace["INSTALLED_APPS"] += SAML_APPS
    namespace["MIDDLEWARE"] += SAML_MIDDLEWARE
