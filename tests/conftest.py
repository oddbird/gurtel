import os

import pytest
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Response


TESTAPP_BASE_DIR = os.path.join(os.path.dirname(__file__), 'testapp')


@pytest.fixture
def testapp_base_dir():
    return TESTAPP_BASE_DIR


def handle_thing(request, thing_id):
    return Response("thing id: %s" % thing_id)


@pytest.fixture
def map_dispatcher():
    from gurtel.dispatch import MapDispatcher
    url_map = Map(
        [
            Rule(r'/thing/<int:thing_id>/', endpoint='thing'),
            Rule(r'/no/handler/', endpoint='nohandler'),
            ]
        )
    handler_map = {
        'thing': handle_thing
    }
    return MapDispatcher(url_map, handler_map)
