from os import path

from cdh.federated_auth.saml.settings import *
from cdh.federated_auth.saml.settings import create_saml_config
from django.urls import reverse_lazy

_BASE_DIR = path.dirname(path.dirname(__file__))


SAML_CONFIG = create_saml_config(
    base_url="http://localhost:8000",
    name="babex",
    key_file=path.join(_BASE_DIR, "certs/private.key"),
    cert_file=path.join(_BASE_DIR, "certs/public.cert"),
    # idp_metadata="https://login.uu.nl/nidp/saml2/metadata",
    idp_metadata="http://localhost:7000/saml/idp/metadata/",
    contact_given_name="Ben",
    contact_email="ben@localhost.local",
)

SAML_ATTRIBUTE_MAPPING = {
    "uushortid": ("username",),
    "mail": ("email",),
    "givenName": ("name",),
    "uuPrefixedSn": ("phonenumber",),
}

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "djangosaml2.backends.Saml2Backend",
)

LOGIN_URL = reverse_lazy("saml2_login")
