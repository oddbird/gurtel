from datetime import timedelta
import json

from werkzeug.contrib.securecookie import SecureCookie

from . import timezone



class JSONSecureCookie(SecureCookie):
    serialization_method = json



def session_middleware(request, response_callable):
    """JSON signed-cookie sessions middleware."""
    request.session = JSONSecureCookie.load_cookie(
        request, secret_key=request.app.secret_key)
    response = response_callable(request)
    request.session.save_cookie(
        response,
        httponly=True,
        secure=request.app.is_ssl,
        expires=timezone.now() + timedelta(days=14),
        )
    return response
