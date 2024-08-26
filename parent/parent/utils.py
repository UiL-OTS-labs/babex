import datetime
import logging
import re
from typing import Optional, Tuple

import jwt
import requests
from django.conf import settings
from django.http.request import HttpRequest
from django.shortcuts import redirect

log = logging.getLogger()


def json_decoder(obj):
    for key, value in obj.items():
        if type(value) == str and re.search(r"\+\d\d:\d\d$", value):
            try:
                obj[key] = datetime.datetime.fromisoformat(value)
            except:
                # maybe it's not a date
                pass
    return obj


def gateway(
    request: HttpRequest, url: str, method: Optional[str] = None, data: Optional[dict] = None
) -> Tuple[bool, dict]:
    """Utility function for making requests to the lab app's gateway.
    Default method is GET, unless data is specified, in which case the default method is POST.
    data is expected to be a json serializable dict
    """

    headers = dict()

    # in the authorization header we store a JWT holding the session token we
    # receive from the lab app after a succesful authentication flow.
    # see mailauth.views.link_verify()
    jwt_token = jwt.encode(
        dict(t=datetime.datetime.now().timestamp(), session=request.session.get("token")),
        key=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    headers["Authorization"] = "Bearer {}".format(jwt_token)

    if method is None:
        if data is not None:
            method = "post"
        else:
            method = "get"

    try:
        response = requests.request(
            method=method.upper(),
            url=settings.API_HOST + url,
            headers=headers,
            json=data,
        )
    except Exception:
        log.exception("Could not reach gateway")
        return False, dict()

    if not response.ok:
        log.error("Gateway request %s failed: %s", url, response.text)
    if len(response.text):
        return response.ok, response.json(object_hook=json_decoder)
    return response.ok, dict()


def session_required(handler):
    # decorator function for limiting views to authenticated users
    def delegate(request, *args, **kwargs):
        if "token" not in request.session:
            return redirect("mailauth:home")
        return handler(request, *args, **kwargs)

    return delegate
