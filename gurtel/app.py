from functools import wraps, partial
import os
import urlparse

from gurtel import assets, dispatch, flash, session, templates
from werkzeug.debug import DebuggedApplication
from werkzeug.exceptions import HTTPException
from werkzeug.utils import cached_property, redirect
from werkzeug.wrappers import Request as WerkzeugRequest
from werkzeug.wsgi import SharedDataMiddleware



def redirect_if(request_test, redirect_to):
    """
    Factory for decorator to redirect if request doesn't pass a test.

    ``request_test`` should be a callable that takes the request and returns a
    boolean.

    ``redirect_to`` should be something that can be passed to the app's
    ``redirect_to`` method.

    If ``request_test`` returns ``False``, will return a redirect to
    ``redirect_to``, otherwise will pass through to the decorated request
    handler.

    """
    def _decorator(func):
        @wraps(func)
        def _inner(request, *args, **kwargs):
            if not request_test(request):
                return request.app.redirect_to(redirect_to)
            return func(request, *args, **kwargs)

        return _inner

    return _decorator



class Request(WerkzeugRequest, flash.FlashRequestMixin):
    pass



class GurtelApp(object):
    """A Gurtel WSGI application."""
    def __init__(self, config, base_dir, dispatcher=None,
                 request_class=Request, middlewares=None,
                 context_processors=None):
        self.config = config
        self.base_dir = base_dir
        self.dispatcher = dispatcher or dispatch.NullDispatcher()
        self.request_class = request_class
        self.middlewares = list(
            middlewares or []) + [session.session_middleware]

        self.base_url = config.get('app.base_url', 'http://localhost')
        bits = urlparse.urlparse(self.base_url)
        self.server_scheme = bits.scheme
        self.server_host = bits.netloc

        self.secret_key = config['app.secret_key']

        self.assets = assets.AssetHandler(
            directory=os.path.join(base_dir, 'static'),
            url=config.get('assets.url', '/static/'),
            minify=config.getbool('assets.minify', True),
            )

        context_processors = list(
            context_processors or []) + [flash.context_processor]
        self.tpl = templates.TemplateRenderer(
            template_dir=os.path.join(base_dir, 'templates'),
            asset_handler=self.assets,
            context_processors=context_processors,
            )

        if config.getbool('app.debugger', False):
            self.wsgi_app = DebuggedApplication(self.wsgi_app, evalex=True)

        if config.getbool('app.serve_static', False):
            self.wsgi_app = SharedDataMiddleware(
                self.wsgi_app, {self.assets.url: self.assets.directory})


    def make_absolute_url(self, url):
        """Make a relative URL absolute by prepending ``self.base_url``."""
        return urlparse.urljoin(self.base_url, url)


    def redirect_to(self, url_or_endpoint, **kwargs):
        """
        Redirect to given URL (made absolute if needed).

        Assumes that a given string with no slashes in it is an endpoint name
        instead of a URL; resolves it with given kwargs.

        """
        if '/' in url_or_endpoint:
            url = url_or_endpoint
        else:
            url = self.url_for(url_or_endpoint, **kwargs)

        return redirect(self.make_absolute_url(url))


    def url_for(self, endpoint, **kwargs):
        """Build a URL for an endpoint and args."""
        return self.dispatcher.url_for(self.server_host, endpoint, **kwargs)


    @cached_property
    def is_ssl(self):
        """Return ``True`` if the app is configured to serve over HTTPS."""
        return self.server_scheme == 'https'


    def wsgi_app(self, environ, start_response):
        """WSGI entry point. Call ``dispatch()``, handle middleware."""
        request = self.request_class(environ)
        request.app = self
        response_callable = self.dispatcher.dispatch
        for middleware in reversed(self.middlewares):
            response_callable = partial(
                middleware, response_callable=response_callable)
        try:
            response = response_callable(request)
        except HTTPException as e:
            response = e
        return response(environ, start_response)


    def __call__(self, environ, start_response):
        """Make the app directly callable."""
        return self.wsgi_app(environ, start_response)
