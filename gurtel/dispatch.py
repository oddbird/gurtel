from werkzeug.exceptions import NotFound
from werkzeug.routing import BuildError



class NullDispatcher(object):
    """A default dispatcher that can't build or dispatch any URLs."""
    def url_for(self, endpoint, **kwargs):
        raise BuildError(endpoint, kwargs, None)


    def dispatch(self, request):
        raise NotFound()



class MapDispatcher(object):
    """Dispatcher that accepts a Map and a mapping of endpoints to handlers."""
    def __init__(self, url_map, handler_map):
        self.url_map = url_map
        self.handler_map = handler_map


    def url_for(self, server_host, endpoint, **kwargs):
        """Build and return URL for given server host, endpoint and kwargs."""
        adapter = self.url_map.bind(server_host)
        return adapter.build(endpoint, kwargs)


    def dispatch(self, request):
        """Dispatch ``request`` and return a ``Response``."""
        adapter = self.url_map.bind_to_environ(request)
        endpoint, kwargs = adapter.match()
        handler = self.handler_map.get(endpoint)
        if handler is None:
            raise NotFound()
        return handler(request, **kwargs)
