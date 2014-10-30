from pretend import stub
import pytest
from werkzeug.contrib.sessions import ModificationTrackingDict as mdt

from gurtel import flash


def test_context_processor():
    """Context processor returns and clears flash messages."""
    msgs = [{'message': 'foo'}]
    req = stub(flash=flash.Flash(mdt(flash=msgs[:])))
    result = flash.context_processor(req)
    assert result.keys() == ['flash']
    assert list(result['flash']) == msgs


def test_request_mixin():
    """Request mixin provides ``flash`` property."""
    class FakeRequest(flash.FlashRequestMixin):
        session = mdt()

    f = FakeRequest()

    assert f.flash.messages == []


@pytest.mark.parametrize('key_exists', [True, False])
def test_send(key_exists):
    """Can send a flash message."""
    kwargs = {'flash': []} if key_exists else {}
    session = mdt(**kwargs)
    f = flash.Flash(session)
    f.send('error', "Some error message")

    assert session['flash'] == [
        {'level': 'error', 'message': "Some error message"}]
    assert session.modified


def test_custom_key():
    """Can set a custom key in the session."""
    session = mdt()
    f = flash.Flash(session, 'messages')
    f.send('info', "Some info")

    assert session['messages'] == [
        {'level': 'info', 'message': "Some info"}]


@pytest.mark.parametrize('level', ['error', 'warning', 'info', 'success'])
def test_level_shortcuts(level):
    """Has shortcut methods for sending messages at certain levels."""
    session = mdt()
    f = flash.Flash(session)
    getattr(f, level)("The message")

    assert session['flash'] == [
        {'level': level, 'message': "The message"}]


def test_get_and_clear():
    """Gets and clears messages."""
    f = flash.Flash(mdt(flash=[{'level': 'error', 'message': "Hello"}]))

    assert list(f.get_and_clear()) == [{'level': 'error', 'message': "Hello"}]
    assert list(f.messages) == []
    assert f.session.modified


def test_partial_get_and_clear():
    """Only clears messages that are actually iterated through."""
    f = flash.Flash(
        mdt(
            flash=[
                {'level': 'error', 'message': "Hello"},
                {'level': 'info', 'message': "Done!"},
            ]
        )
    )

    iterator = f.get_and_clear()
    assert iterator.next()['level'] == 'info'
    assert len(f.messages) == 1
    assert f.session.modified
