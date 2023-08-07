import logging

from .models import lookup_session_token

log = logging.getLogger()


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
        request.participant = None
        if auth := request.headers.get("Authorization"):
            try:
                token = auth.split(" ")[1]
                participant = lookup_session_token(token)

                # make sure the participant wasn't deactivated
                if participant.deactivated is None:
                    request.participant = participant
            except Exception:
                log.exception("Error while processing authorization header: %s", auth)

        return self.get_response(request)
