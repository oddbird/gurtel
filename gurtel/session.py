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
    cookie_kwargs = {
        'httponly': True,
        'secure': request.app.is_ssl,
    }
    expiry_minutes = int(
        request.app.config.get('session.expiry_minutes', 0))
    if expiry_minutes:
        delta = timedelta(minutes=expiry_minutes)
        cookie_kwargs['expires'] = timezone.now() + delta
    request.session.save_cookie(response, **cookie_kwargs)
    return response
