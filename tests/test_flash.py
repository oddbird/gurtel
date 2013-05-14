import pytest

from gurtel import flash


def test_request_mixin():
    """Request mixin provides ``flash`` property."""
    class FakeRequest(flash.FlashRequestMixin):
        session = {}

    f = FakeRequest()

    assert f.flash.messages == []


def test_send():
    """Can send a flash message."""
    session = {}
    f = flash.Flash(session)
    f.send('error', "Some error message")

    assert session['flash'] == [
        {'level': 'error', 'message': "Some error message"}]


def test_custom_key():
    """Can set a custom key in the session."""
    session = {}
    f = flash.Flash(session, 'messages')
    f.send('info', "Some info")

    assert session['messages'] == [
        {'level': 'info', 'message': "Some info"}]


@pytest.mark.parametrize('level', ['error', 'warning', 'info', 'success'])
def test_level_shortcuts(level):
    """Has shortcut methods for sending messages at certain levels."""
    session = {}
    f = flash.Flash(session)
    getattr(f, level)("The message")

    assert session['flash'] == [
        {'level': level, 'message': "The message"}]


def test_get_and_clear():
    """Gets and clears messages."""
    f = flash.Flash({'flash': [{'level': 'error', 'message': "Hello"}]})

    assert list(f.get_and_clear()) == [{'level': 'error', 'message': "Hello"}]
    assert list(f.messages) == []


def test_partial_get_and_clear():
    """Only clears messages that are actually iterated through."""
    f = flash.Flash(
        {
            'flash': [
                {'level': 'error', 'message': "Hello"},
                {'level': 'info', 'message': "Done!"},
                ]
            }
        )

    iterator = f.get_and_clear()
    assert iterator.next()['level'] == 'info'
    assert len(f.messages) == 1
