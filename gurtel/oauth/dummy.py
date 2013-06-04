"""Dummy OAuth handler for testing and local development."""
from .base import OAuthBase



class DummyOAuth(OAuthBase):
    """
    Dummy OAuth backend.

    Rather than redirecting to an external OAuth provider, this backend
    redirects to a URL provided by its own WSGI app wrapper (``DummyOAuthApp``)
    that displays a form for entering user data.

    """
    def __init__(self, redirect_uri, **kwargs):
        self.redirect_uri = redirect_uri


    def get_authorize_url(self):
        """Return the authorization URL at the OAuth provider."""
        return DUMMY_FORM_URL


    def get_user_data(self, request_args):
        """
        Return dictionary of data about newly-OAuth-authenticated user.

        ``request_args`` is a dictionary of querystring data from the redirect
        from the OAuth provider.

        """
        return dict(request_args.iteritems())


    def wrap_app(self, app):
        """Wrap a WSGI app with DummyOAuthApp."""
        return DummyOAuthApp(app, self.redirect_uri)



DUMMY_FORM_URL = '/__dummy_oauth/'


class DummyOAuthApp(object):
    """A WSGI wrapper app to intercept the dummy OAuth user-data form url."""
    def __init__(self, wrapped_app, redirect_uri):
        self.wrapped_app = wrapped_app
        self.redirect_uri = redirect_uri


    def __call__(self, environ, start_response):
        if environ['PATH_INFO'] == DUMMY_FORM_URL:
            response = USER_FORM % {'redirect_uri': self.redirect_uri}
            response = response.encode('utf-8')
            headers = [
                ('Content-Type', 'text/html; charset=utf-8'),
                ('Content-Length', str(len(response)))
                ]
            status = '200 OK'
            start_response(status, headers)
            return [response]
        return self.wrapped_app(environ, start_response)



USER_FORM = u"""
<html>
<head>
<title>Dummy OAuth login form</title>
</head>
<body>
<form id='dummy-oauth-form' method="GET" action="%(redirect_uri)s">
Username: <input type="text" name="username">
Email: <input type="text" name="email">
Name: <input type="text" name="name">
<button type="submit">Submit</button>
</form>
</body>

"""
