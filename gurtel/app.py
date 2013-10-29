from functools import wraps, partial
import logging
import logging.config
import os
import urlparse

from gurtel.assets import get_bundles
from gurtel import flash, session
from jinja2 import Environment, FileSystemLoader
from webassets import Environment as AssetsEnvironment
from webassets.ext.jinja2 import AssetsExtension
from werkzeug.debug import DebuggedApplication
from werkzeug.exceptions import HTTPException
from werkzeug.routing import Map
from werkzeug.utils import cached_property, redirect
from werkzeug.wrappers import Response, Request as WerkzeugRequest
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
        def _inner(app, request, *args, **kwargs):
            if not request_test(request):
                return app.redirect_to(redirect_to)
            return func(app, request, *args, **kwargs)

        return _inner

    return _decorator



class GurtelApp(object):
    """Base class for a Gurtel WSGI application."""
    def __init__(self, config, base_dir, db_class):
        self.config = config

        self.middlewares = [
            session.session_middleware,
            ]

        self.base_url = config.get('app.base_url', 'http://localhost')
        bits = urlparse.urlparse(self.base_url)
        self.server_scheme = bits.scheme
        self.server_host = bits.netloc

        self.secret_key = config['app.secret_key']

        self.db = db_class(config['database.uri'])

        static_dir = os.path.join(base_dir, 'static')
        static_url = '/static/'

        self.jinja_env = Environment(
            loader=FileSystemLoader(os.path.join(base_dir, 'templates')),
            autoescape=True,
            extensions=[AssetsExtension],
            )
        self.assets_env = AssetsEnvironment(
            static_dir,
            static_url,
            debug=not config.getbool('assets.minify', True),
            )
        self.assets_env.register(
            get_bundles(os.path.join(static_dir, 'bundles.yml')))
        self.jinja_env.assets_environment = self.assets_env

        self.url_map = Map()

        if config.getbool('app.debugger', False):
            self.wsgi_app = DebuggedApplication(self.wsgi_app, evalex=True)

        if config.getbool('app.serve_static', False) and static_dir:
            self.wsgi_app = SharedDataMiddleware(
                self.wsgi_app, {static_url: static_dir})


    def configure_logging(self, disable_existing=False):
        """
        Set up loggers according to app configuration.

        Since this impacts global state, we don't do it by default in app init;
        caller has to explicitly request it.

        """
        logging_config = self.config.getpath('app.logging', None)
        if logging_config is not None:
            logging.config.fileConfig(
                logging_config, disable_existing_loggers=disable_existing)


    def render(self, request, template_name, context=None, mimetype='text/html'):
        """Request-aware template render."""
        context = context or {}
        context['flash'] = request.flash.get_and_clear()
        return self.render_template(template_name, context, mimetype)


    def render_template(self, template_name, context=None, mimetype='text/html'):
        """Render ``template_name`` with ``context`` and ``mimetype``."""
        context = context or {}
        context['app'] = self
        tpl = self.jinja_env.get_template(template_name)
        return Response(tpl.render(context), mimetype=mimetype)


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
        adapter = self.url_map.bind(self.server_host)
        return adapter.build(endpoint, kwargs)


    @cached_property
    def is_ssl(self):
        """Return ``True`` if the app is configured to serve over HTTPS."""
        return self.server_scheme == 'https'


    def get_request_class(self):
        """Construct and return Request subclass for this app."""
        class Request(WerkzeugRequest, flash.FlashRequestMixin):
            pass

        return Request


    @cached_property
    def request_class(self):
        """Request subclass for this app."""
        return self.get_request_class()


    def dispatch(self, request):
        """Dispatch request according to URL map, return response."""
        adapter = self.url_map.bind_to_environ(request)
        try:
            endpoint, args = adapter.match()
            handler = getattr(self, 'handle_' + endpoint)
            return handler(request, **args)
        except HTTPException as e:
            return e


    def wsgi_app(self, environ, start_response):
        """WSGI entry point. Call ``dispatch()``, handle middleware."""
        request = self.request_class(environ)
        request.app = self
        response_callable = self.dispatch
        for middleware in reversed(self.middlewares):
            response_callable = partial(
                middleware, response_callable=response_callable)
        response = response_callable(request)
        return response(environ, start_response)


    def __call__(self, environ, start_response):
        """Make the app directly callable."""
        return self.wsgi_app(environ, start_response)
