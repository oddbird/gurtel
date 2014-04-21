import datetime

from mock import patch
from pretend import stub

from gurtel import session


def test_annotates_request():
    """Annotates request with ``session`` property."""
    request = stub(
        cookies={},
        app=stub(secret_key='secret', is_ssl=True, config={}),
        )

    session.session_middleware(request, lambda req: None)

    assert request.session.secret_key == 'secret'


@patch.object(session.JSONSecureCookie, 'save_cookie')
def test_sets_cookie_on_response(mock_save_cookie):
    """Calls ``save_cookie`` on response."""
    request = stub(
        cookies={},
        app=stub(secret_key='secret', is_ssl=True, config={}),
        )
    response = stub()

    session.session_middleware(request, lambda req: response)

    mock_save_cookie.assert_called_once_with(
        response, httponly=True, secure=True)


@patch.object(session.JSONSecureCookie, 'save_cookie')
@patch.object(session.timezone, 'now')
def test_can_set_expiry(mock_now, mock_save_cookie):
    """Calls ``save_cookie`` on response with expiry date, if configured."""
    request = stub(
        cookies={},
        app=stub(
            secret_key='secret',
            is_ssl=True,
            config={'session.expiry_minutes': '1440'},
        ),
    )
    response = stub()

    mock_now.return_value = datetime.datetime(2013, 11, 22)

    session.session_middleware(request, lambda req: response)

    mock_save_cookie.assert_called_once_with(
        response,
        httponly=True,
        secure=True,
        expires=datetime.datetime(2013, 11, 23),
    )
