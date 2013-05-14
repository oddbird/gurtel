import pytest

from gurtel.oauth.base import OAuthBase


def test_get_authorize_url_not_implemented():
    with pytest.raises(NotImplementedError):
        OAuthBase().get_authorize_url()


def test_get_user_data_not_implemented():
    with pytest.raises(NotImplementedError):
        OAuthBase().get_user_data('redirect_url')


def test_wrap_app_is_noop():
    x = object()
    assert OAuthBase().wrap_app(x) is x
