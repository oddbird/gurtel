from werkzeug.exceptions import NotFound
from werkzeug.routing import BuildError
from werkzeug.test import EnvironBuilder

import pytest

from gurtel import dispatch



class TestNullDispatcher(object):
    def test_url_for(self):
        """url_for method always raises BuildError."""
        with pytest.raises(BuildError):
            dispatch.NullDispatcher().url_for('foo')


    def test_dispatch(self):
        """dispatch method always returns NotFound response."""
        with pytest.raises(NotFound):
            dispatch.NullDispatcher().dispatch(None)



class TestMapDispatcher(object):
    def test_url_for(self, map_dispatcher):
        """Builds and returns URL for given host/endpoint/kwargs."""
        url = map_dispatcher.url_for('loc', 'thing', thing_id=4)
        assert url == '/thing/4/'


    def test_dispatch(self, map_dispatcher):
        """Dispatches request and returns response."""
        request = EnvironBuilder('/thing/2/').get_environ()
        response = map_dispatcher.dispatch(request)
        assert response.data == 'thing id: 2'


    def test_dispatch_no_handler(self, map_dispatcher):
        """Raises NotFound if no handler is found for endpoint."""
        request = EnvironBuilder('/no/handler/').get_environ()
        with pytest.raises(NotFound):
            map_dispatcher.dispatch(request)
