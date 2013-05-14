from datetime import timedelta
import json

from werkzeug.contrib.securecookie import SecureCookie

from . import timezone



class JSONSecureCookie(SecureCookie):
    serialization_method = json



class SessionMiddleware(object):
    """JSON signed-cookie sessions middleware."""
    def process_request(self, app, request):
        """Annotate the request with a session property."""
        request.session = JSONSecureCookie.load_cookie(
            request, secret_key=app.secret_key)


    def process_response(self, app, request, response):
        """Save the session cookie if session changed."""
        request.session.save_cookie(
            response,
            httponly=True,
            secure=app.is_ssl,
            expires=timezone.now() + timedelta(days=14),
            )
