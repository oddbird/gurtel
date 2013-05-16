import os

import mock
from pretend import stub
import pytest
from werkzeug.routing import Map, Rule
from werkzeug.test import Client, EnvironBuilder
from werkzeug.wrappers import Response

from gurtel.app import redirect_if, GurtelApp
from gurtel.config import Config


class FakeApp(object):
    def __init__(self):
        self.redirects = []
        self.handled = []

    def redirect_to(self, redirect_to):
        self.redirects.append(redirect_to)


TESTAPP_BASE_DIR = os.path.join(os.path.dirname(__file__), 'testapp')


class TestRedirectIf(object):
    def test_redirect(self):
        """If request fails test, redirects."""
        app = self.make_app(redirect_if(lambda req: False, 'login'))

        app.handler(None, 1, foo=2)

        assert app.redirects == ['login']
        assert app.handled == []


    def test_no_redirect(self):
        """If request passes test, does not redirect."""
        app = self.make_app(redirect_if(lambda req: True, 'login'))

        req = stub()

        app.handler(req, 1, foo=2)

        assert app.redirects == []
        assert app.handled == [((req, 1), {'foo': 2})]


    def make_app(self, deco):
        """Make a fake app with decorated handler method."""
        class App(FakeApp):
            @deco
            def handler(self, *a, **kw):
                self.handled.append((a, kw))

        app = App()

        return app


class TestGurtelAppConfig(object):
    """Tests for configuration of Gurtel app."""
    def test_db_uri(self):
        """Database URI passed through app to Database."""
        db_class = lambda db_uri: stub(uri=db_uri)
        app = self.get_app({'database.uri': 'sqlite:///'}, db_class)

        assert app.db.uri == 'sqlite:///'

    def test_base_url(self):
        """Base url passed in from config."""
        app = self.get_app({'app.base_url': 'https://example.com'})

        assert app.base_url == 'https://example.com'
        assert app.server_scheme == 'https'
        assert app.server_host == 'example.com'


    @mock.patch('gurtel.app.DebuggedApplication')
    @pytest.mark.parametrize('tf', [True, False])
    def test_debugger(self, mock_DebuggedApplication, tf):
        """Debugger enabled only if configured."""
        self.get_app({'app.debugger': str(tf)})

        assert bool(mock_DebuggedApplication.call_count) == tf


    @mock.patch('gurtel.app.SharedDataMiddleware')
    @pytest.mark.parametrize('tf', [True, False])
    def test_static(self, mock_SharedDataMiddleware, tf):
        """Static files serving enabled only if configured."""
        self.get_app({'app.serve_static': str(tf)})

        assert bool(mock_SharedDataMiddleware.call_count) == tf


    @mock.patch('logging.config.fileConfig')
    def test_logging(self, mock_fileConfig):
        """Configures logging if app.logging config key found."""
        app = self.get_app({'app.logging': 'logging.ini'})
        app.configure_logging()

        mock_fileConfig.assert_called_once_with(
            'logging.ini',
            disable_existing_loggers=False,
            )


    @mock.patch('logging.config.fileConfig')
    def test_no_logging(self, mock_fileConfig):
        """Does not configure logging if no config key found."""
        app = self.get_app({})
        app.configure_logging()

        assert mock_fileConfig.call_count == 0


    def get_app(self, config_dict, db_class=None):
        """Shortcut for creating app with given config data."""
        config_dict.setdefault('app.secret_key', 'secret')
        config_dict.setdefault('database.uri', 'sqlite:///')
        if db_class is None:
            db_class = lambda db_uri: None
        return GurtelApp(Config(config_dict), TESTAPP_BASE_DIR, db_class)


class GurtelTestApp(GurtelApp):
    def __init__(self, config):
        super(GurtelTestApp, self).__init__(
            config, TESTAPP_BASE_DIR, lambda db_uri: None)

        self.url_map = Map([
                Rule(r'/thing/<int:thing_id>/', endpoint='thing'),
                ])


    def handle_thing(self, request, thing_id):
        return self.render_template('thing.html', {'thing_id': thing_id})



@pytest.fixture
def app(request, config):
    return GurtelTestApp(config)


@pytest.fixture
def client(request, app):
    return Client(app, Response)


@pytest.fixture
def req(request, app):
    environ = EnvironBuilder().get_environ()
    req = app.request_class(environ)
    req.session = {}

    return req


class TestGurtelApp(object):
    """Unit tests for app utility methods."""
    @pytest.mark.config({'app.base_url': 'http://somehost'})
    def test_make_absolute_url(self, app):
        """Turns relative url into absolute by prepending base_url."""
        assert app.make_absolute_url('/foo/') == 'http://somehost/foo/'


    @pytest.mark.config({'app.base_url': 'http://somehost'})
    def test_redirect_to(self, app):
        """Given relative URL, returns redirect response to absolute URL."""
        response = app.redirect_to('/foo/')

        assert response.status_code == 302
        assert response.headers['location'] == 'http://somehost/foo/'


    @pytest.mark.config({'app.base_url': 'http://somehost'})
    def test_redirect_to_reverses_url(self, app):
        """Given endpoint, returns redirect to reversed URL."""
        response = app.redirect_to('thing', thing_id=2)

        assert response.status_code == 302
        assert response.headers['location'] == 'http://somehost/thing/2/'


    def test_redirect_to_absolute(self, app):
        """Given absolute URL, returns redirect to it."""
        response = app.redirect_to('https://www.example.com/bar/')

        assert response.status_code == 302
        assert response.headers['location'] == 'https://www.example.com/bar/'


    def test_url_for(self, app):
        """Given endpoint, returns URL for that endpoint."""
        assert app.url_for('thing', thing_id=1) == '/thing/1/'


    def test_url_for_with_args(self, app):
        """Given endpoint and keyword args, returns URL."""
        assert app.url_for('thing', thing_id=3) == '/thing/3/'


    @pytest.mark.config({'app.base_url': 'https://somehost'})
    def test_is_ssl(self, app):
        """If base_url scheme is https, ``is_ssl`` is ``True``."""
        assert app.is_ssl


    @pytest.mark.config({'app.base_url': 'http://somehost'})
    def test_is_not_ssl(self, app):
        """If base_url scheme is not https, ``is_ssl`` is ``False``."""
        assert not app.is_ssl


    def test_render_custom_mime_type(self, app, req):
        """Render can take a custom mime type."""
        resp = app.render(req, 'text.txt', mimetype='text/plain')

        assert resp.mimetype == 'text/plain'


    def test_render_template_custom_mime_type(self, app):
        """Render template can take a custom mime type."""
        resp = app.render_template('text.txt', mimetype='text/plain')

        assert resp.mimetype == 'text/plain'


    def test_render_flash(self, app, req):
        """Adds flash messages to template context."""
        req.flash.success('yay for you.')
        resp = app.render(req, 'flash.html')

        assert resp.data == '\n  yay for you.\n'


    def test_dispatch_and_render(self, client, app):
        """Can dispatch to a URL, render template, return response."""
        resp = client.get(app.url_for('thing', thing_id=3))

        assert resp.data == 'thing id: 3'


    def test_404(self, client):
        """Unknown URL returns 404 status."""
        resp = client.get('/foo/')

        assert resp.status_code == 404


    def test_incomplete_middleware(self, client, app):
        """Can handle middleware without process_* methods."""
        class DummyMiddleware(object): pass

        app.middlewares.append(DummyMiddleware())

        client.get('/')
