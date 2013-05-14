from pretend import stub
import pytest
from werkzeug.test import Client
from werkzeug.wrappers import Response

from gurtel.oauth import dummy



@pytest.fixture
def client(request):
    def wrapped(environ, start_response):
        return Response("Wrapped app")(environ, start_response)
    return Client(dummy.DummyOAuthApp(wrapped, '/redirect/'), Response)



def test_get_authorize_url():
    """Returns the dummy form URL."""
    o = dummy.DummyOAuth('/redirect/')

    assert o.get_authorize_url() == dummy.DUMMY_FORM_URL



def test_get_user_data():
    """Just returns copy of given query args."""
    o = dummy.DummyOAuth('/redirect/')

    assert o.get_user_data({'foo': 'bar'}) == {'foo': 'bar'}



def test_wrap_app():
    """Wraps given app with ``DummyOAuthApp``."""
    o = dummy.DummyOAuth('/redirect/')
    app = stub()

    wrapper = o.wrap_app(app)

    assert wrapper.wrapped_app is app
    assert wrapper.redirect_uri == '/redirect/'


def test_dummy_app_form(client):
    """Request to dummy form URL returns form."""
    resp = client.get(dummy.DUMMY_FORM_URL)

    assert resp.data == dummy.USER_FORM % {
        'redirect_uri': '/redirect/'}


def test_dummy_app_passthrough(client):
    """Request to other URL passed through to wrapped app."""
    resp = client.get('/other/')

    assert resp.data == "Wrapped app"
