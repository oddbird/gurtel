from mock import patch
from pretend import stub

from gurtel import session


def test_annotates_request():
    """Annotates request with ``session`` property."""
    request = stub(
        cookies={},
        app=stub(secret_key='secret', is_ssl=True),
        )

    session.session_middleware(request, lambda req: None)

    assert request.session.secret_key == 'secret'


@patch.object(session.JSONSecureCookie, 'save_cookie')
def test_sets_cookie_on_response(mock_save_cookie):
    """Calls ``save_cookie`` on response."""
    request = stub(
        cookies={},
        app=stub(secret_key='secret', is_ssl=True),
        )
    response = stub()

    session.session_middleware(request, lambda req: response)

    assert mock_save_cookie.call_args[0] == (response,)
    assert mock_save_cookie.call_args[1]['httponly'] is True
    assert mock_save_cookie.call_args[1]['secure'] is True
