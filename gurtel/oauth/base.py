class OAuthError(Exception):
    pass


class OAuthBase(object):
    """Abstract base for OAuth backends."""
    def __init__(self, **kwargs):
        pass


    def get_authorize_url(self):
        """Return the authorization url at the OAuth provider."""
        raise NotImplementedError()


    def get_user_data(self, request_args):
        """
        Return dict of data about newly-authenticated OAuth user.

        ``request_args`` is a dictionary of querystring data from the redirect
        from the OAuth provider.

        """
        raise NotImplementedError()


    def wrap_app(self, app):
        """Hook for OAuth backend to wrap a WSGI app."""
        return app
