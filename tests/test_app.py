import mock
from pretend import stub
import pytest
from werkzeug.test import Client, EnvironBuilder
from werkzeug.wrappers import Response

from gurtel.app import redirect_if, GurtelApp
from gurtel.config import Config

from .conftest import TESTAPP_BASE_DIR


class FakeApp(object):
    def __init__(self):
        self.redirects = []
        self.handled = []

    def redirect_to(self, redirect_to):
        self.redirects.append(redirect_to)


class TestRedirectIf(object):
    def test_redirect(self):
        """If request fails test, redirects."""
        app = FakeApp()
        h = self.make_handler(redirect_if(lambda req: False, 'login'))

        h(stub(app=app), 1, foo=2)

        assert app.redirects == ['login']
        assert app.handled == []

    def test_no_redirect(self):
        """If request passes test, does not redirect."""
        app = FakeApp()
        h = self.make_handler(redirect_if(lambda req: True, 'login'))

        h(stub(app=app), 1, foo=2)

        assert app.redirects == []
        assert app.handled == [((1, ), {'foo': 2})]

    def make_handler(self, deco):
        """Return a decorated handler function."""
        @deco
        def handler(request, *a, **kw):
            request.app.handled.append((a, kw))

        return handler


class TestGurtelAppConfig(object):
    """Tests for configuration of Gurtel app."""
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

    def get_app(self, config_dict):
        """Shortcut for creating app with given config data."""
        config_dict.setdefault('app.secret_key', 'secret')
        return GurtelApp(Config(config_dict), TESTAPP_BASE_DIR)


@pytest.fixture
def app(request, config, map_dispatcher):
    return GurtelApp(config, TESTAPP_BASE_DIR, map_dispatcher)


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

    def test_dispatch_and_render(self, client, app):
        """Can dispatch to a URL, render template, return response."""
        resp = client.get(app.url_for('thing', thing_id=3))

        assert resp.data == 'thing id: 3'

    def test_404(self, client):
        """Unknown URL returns 404 status."""
        resp = client.get('/foo/')

        assert resp.status_code == 404
