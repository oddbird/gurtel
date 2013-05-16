import os

import pytest


def pytest_addoption(parser):
    group = parser.getgroup("OddBooks")
    group.addoption(
        "--config",
        dest="config",
        help="A .ini file with config for running tests",
    )


@pytest.fixture(scope='session')
def _base_config(request):
    from gurtel.config import Config

    config = Config().read_from_file(request.config.getvalueorskip('config'))

    logging_config = config.getpath('app.logging', None)
    if logging_config is not None:
        import logging
        logging.config.fileConfig(
            logging_config, disable_existing_loggers=False)

    return config


@pytest.fixture
def config(request, _base_config):
    config = _base_config.copy()

    if 'config' in request.keywords:
        config.update(request.keywords['config'].args[0].items())

    return config


@pytest.fixture
def configfile(request, tmpdir):
    """
    Write a temporary config file.

    Config file takes contents from ``configfile_contents`` mark, otherwise is
    empty.

    """
    if 'configfile_contents' in request.keywords:
        contents = request.keywords['configfile_contents'].args[0]
    else:
        contents = ''

    fn = os.path.join(str(tmpdir), 'config.ini')
    with open(fn, 'w') as fh:
        fh.write(contents)

    return fn
