from .models import lookup_session_token


class SessionTokenMiddleware:
    """Looks for a session token on incoming requests, and sets request.participant
    to the relevant Participant when the session is valid.

    As a middleware, this applies to all requests, but it is actually intended to be
    used with (only) gateway requests, where the parent app makes requests to the lab app
    on behalf of an authenticated parent.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            request.participant = lookup_session_token(token)
        except Exception:
            request.participant = None

        return self.get_response(request)
