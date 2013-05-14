"""Session-based flash messaging."""
from werkzeug.utils import cached_property



class FlashRequestMixin(object):
    """
    Request mixin that provides ``request.flash`` property.

    Requires request object to have a ``self.session`` property that is a
    dictionary-like object.

    """
    @cached_property
    def flash(self):
        return Flash(self.session)



class Flash(object):
    """
    Session-based flash messaging.

    Instantiate with a session (any dictionary-like object) and a key to use in
    the session (defaults to 'flash').

    """
    def __init__(self, session, key='flash'):
        self.session = session
        self.key = key


    @cached_property
    def messages(self):
        return self.session.setdefault(self.key, [])


    def send(self, level, message):
        """Send a flash message."""
        # We iterate through messages in reverse order due to the use of pop(),
        # so inserting at the beginning preserves FIFO.
        self.messages.insert(0, {'level': level, 'message': message})


    def success(self, message):
        """Shortcut for sending a message with level 'success'."""
        self.send('success', message)


    def info(self, message):
        """Shortcut for sending a message with level 'success'."""
        self.send('info', message)


    def warning(self, message):
        """Shortcut for sending a message with level 'success'."""
        self.send('warning', message)


    def error(self, message):
        """Shortcut for sending a message with level 'success'."""
        self.send('error', message)


    def get_and_clear(self):
        while self.messages:
            yield self.messages.pop()
