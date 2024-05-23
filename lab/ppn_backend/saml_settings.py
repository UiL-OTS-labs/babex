from os import getenv

from cdh.federated_auth.saml.settings import (
    SAML_APPS,
    SAML_MIDDLEWARE,
    create_saml_config,
)
from django.urls import reverse_lazy


def enable_saml(namespace):
    namespace["SAML_CONFIG"] = create_saml_config(
        base_url="https://" + getenv("LAB_SERVER"),
        name="babex",
        key_file="/run/secrets/SAML_KEY",
        cert_file="/run/secrets/SAML_CERT",
        idp_metadata=getenv("SAML_IDP_METADATA"),
        contact_given_name=getenv("SAML_CONTACT_NAME"),
        contact_email=getenv("SAML_CONTACT_EMAIL")
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
