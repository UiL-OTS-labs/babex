from typing import Optional, Tuple

import requests
from django.conf import settings
from django.http.request import HttpRequest
from django.shortcuts import redirect


def gateway(
    request: HttpRequest, url: str, method: Optional[str] = None, data: Optional[dict] = None
) -> Tuple[bool, dict]:
    """Utility function for making requests to the lab app's gateway.
    Default method is GET, unless data is specified, in which case the default method is POST.
    data is expected to be a json serializable dict
    """

    headers = dict()
    if "token" in request.session:
        # in the authorization header we store the session token we
        # receive from the lab app after a succesful authentication flow.
        # see mailauth.views.link_verify()
        headers["Authorization"] = "Bearer {}".format(request.session["token"])

    if method is None:
        if data is not None:
            method = "post"
        else:
            method = "get"

    response = requests.request(
        method=method.upper(),
        url=settings.API_HOST + url,
        headers=headers,
        json=data,
    )
    return response.ok, response.json()


def session_required(handler):
    # decorator function for limiting views to authenticated users
    def delegate(request, *args, **kwargs):
        if "token" not in request.session:
            return redirect("mailauth:home")
        return handler(request, *args, **kwargs)

    return delegate
