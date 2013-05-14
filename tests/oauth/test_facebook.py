import json

import mock
import pytest

from gurtel.oauth import facebook, OAuthError
from gurtel.util import Url


@pytest.fixture
def fbo(request):
    return facebook.FacebookOAuth(
        redirect_uri='http://www.example.com/oauth/',
        client_id='client-id',
        client_secret='client-secret',
        )


def test_get_authorize_url(fbo):
    assert Url(fbo.get_authorize_url()) == Url(
        'https://graph.facebook.com/oauth/authorize?'
        'client_id=client-id&scope=email&'
        'redirect_uri=http://www.example.com/oauth/'
        )


def test_get_user_data(fbo, monkeypatch):
    """Gets access token using code, gets profile data via access token."""
    monkeypatch.setattr(fbo, 'get_access_token', mock.Mock())
    monkeypatch.setattr(fbo, 'get_profile', mock.Mock())

    user_data = fbo.get_user_data({'code': 'mock-code'})

    fbo.get_access_token.assert_called_once_with('mock-code')
    fbo.get_profile.assert_called_once_with(fbo.get_access_token.return_value)
    assert user_data is fbo.get_profile.return_value


def test_get_user_data_no_code(fbo):
    """Errors if no code in OAuth request args."""
    with pytest.raises(OAuthError):
        fbo.get_user_data({})


def test_get_access_token(fbo, monkeypatch):
    """Gets access token given valid code."""
    monkeypatch.setattr(facebook.requests, 'get', mock.Mock())
    response = facebook.requests.get.return_value
    response.text = 'access_token=foo'
    response.status_code = 200

    assert fbo.get_access_token('mock-code')
    facebook.requests.get.assert_called_once_with(
        'https://graph.facebook.com/oauth/access_token',
        params={
            'client_id': 'client-id',
            'client_secret': 'client-secret',
            'code': 'mock-code',
            'redirect_uri': 'http://www.example.com/oauth/',
            }
        )


def test_get_access_token_error(fbo, monkeypatch):
    """If getting access token results in error, raises OAuthError."""
    monkeypatch.setattr(facebook.requests, 'get', mock.Mock())
    response = facebook.requests.get.return_value
    response.text = json.dumps(
        {
            'error': {
                'message': "Some error message",
                'type': "OAuthException",
                'code': 191,
                },
            }
        )
    response.status_code = 400

    with pytest.raises(OAuthError) as e:
        fbo.get_access_token('mock-code')

    assert str(e.value) == "Some error message"


def test_get_profile(fbo, monkeypatch):
    """Gets profile data given valid access token."""
    monkeypatch.setattr(facebook.requests, 'get', mock.Mock())
    retval = {'email': 'someone@example.com'}
    facebook.requests.get.return_value.json.return_value = retval

    assert fbo.get_profile('mock-token') == retval
    facebook.requests.get.assert_called_once_with(
        'https://graph.facebook.com/me?'
        'fields=username,first_name,middle_name,last_name,name,locale,gender,'
        'timezone,email',
        params={'access_token': 'mock-token'},
        )


def test_get_profile_only_returns_requested_fields(fbo, monkeypatch):
    """Only returns fields set in ``profile_fields`` class attr."""
    monkeypatch.setattr(facebook.requests, 'get', mock.Mock())
    retval = {'email': 'someone@example.com', 'foo': 'bar'}
    facebook.requests.get.return_value.json.return_value = retval

    assert fbo.get_profile('mock-token') == {'email': 'someone@example.com'}
