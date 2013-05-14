from pretend import stub

from gurtel import session


def test_process_request():
    """Annotates request with ``session`` property."""
    app = stub(secret_key='secret')
    request = stub(cookies={})
    middleware = session.SessionMiddleware()

    middleware.process_request(app, request)

    assert request.session.secret_key == 'secret'



def test_process_response():
    """Calls ``save_cookie`` on response."""
    app = stub(is_ssl=True)
    call_args = []
    request = stub(
        session=stub(save_cookie=lambda *a, **kw: call_args.append((a, kw))))
    response = stub()
    middleware = session.SessionMiddleware()

    middleware.process_response(app, request, response)

    assert call_args[0][0] == (response,)
    assert call_args[0][1]['httponly'] is True
    assert call_args[0][1]['secure'] is True
