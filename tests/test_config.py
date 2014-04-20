import os

import pytest

from gurtel.config import Config


@pytest.mark.configfile_contents("[database]\nuri = sqlite:///")
def test_read_from_file(configfile):
    c = Config().read_from_file(configfile)

    assert c.data == {'database.uri': 'sqlite:///'}


def test_read_from_env():
    """``read_from_env`` reads env vars with given prefix only."""
    c = Config().read_from_env(
        prefix='ODDTILES_',
        env={
            'ODDTILES_APP__BASE_URL': 'http://somehost',
            'NO_PREFIX__SOMETHING': 'unrelated',
            },
        )

    assert c['app.base_url'] == 'http://somehost'
    assert c.keys() == ['app.base_url']


def test_read_from_os_environ(monkeypatch):
    """``read_from_env`` reads from ``os.environ`` by default."""
    fake_environ = {'ODDTILES_APP__BASE_URL': 'http://somehost'}

    monkeypatch.setattr(os, 'environ', fake_environ)

    c = Config().read_from_env(prefix='ODDTILES_')

    assert c['app.base_url'] == 'http://somehost'
    assert c.keys() == ['app.base_url']


def test_update():
    """Can update config from a dict."""
    c = Config()
    c.update({'app.secret_key': 'foo'})

    assert c['app.secret_key'] == 'foo'


def test_copy():
    """Can copy a config."""
    c = Config({'app.secret_key': 'foo'})
    d = c.copy()
    d.update({'app.base_url': 'http://somehost'})

    assert 'app.base_url' not in c
    assert d['app.secret_key'] == 'foo'


def test_get():
    c = Config({'db.uri': 'sqlite:///'})

    assert c.get('db.uri') == 'sqlite:///'


def test_get_nonexistent():
    c = Config()

    assert c.get('db.uri') is None


def test_containment():
    c = Config({'db.uri': 'sqlite:///'})

    assert 'db.uri' in c
    assert 'something.else' not in c


def test_keys():
    c = Config({'db.uri': 'sqlite:///'})

    assert c.keys() == ['db.uri']


def test_get_default():
    c = Config()

    assert c.get('db.uri', 'sqlite:///') == 'sqlite:///'


def test_getitem():
    c = Config({'db.uri': 'sqlite:///'})

    assert c['db.uri'] == 'sqlite:///'


def test_getitem_nonexistent():
    c = Config()

    with pytest.raises(KeyError):
        c['db.uri']


@pytest.mark.parametrize(
    'val',
    ['y', 'Y', 'Yes', 'yes', 'YES', 'T', 't', 'TRUE', 'true', '1', 'ON', 'on']
    )
def test_getbool_true(val):
    c = Config({'app.debug': val})

    assert c.getbool('app.debug') is True


@pytest.mark.parametrize(
    'val',
    ['n', 'N', 'No', 'no', 'NO', 'F', 'f', 'FALSE', 'false', '0', 'OFF', 'off']
    )
def test_getbool_false(val):
    c = Config({'app.debug': val})

    assert c.getbool('app.debug') is False


@pytest.mark.parametrize('val', ['', 'bad', '3'])
def test_getbool_bad(val):
    c = Config({'app.debug': val})

    with pytest.raises(ValueError):
        c.getbool('app.debug')


@pytest.mark.parametrize('method', ['getbool', 'getpath'])
def test_nonexistent_keyerror(method):
    c = Config()

    with pytest.raises(KeyError):
        getattr(c, method)('app.debug')


def test_getbool_default():
    c = Config()

    assert c.getbool('app.debug', False) is False


@pytest.mark.configfile_contents('[app]\nlogging=logging.ini')
def test_getpath(configfile):
    c = Config().read_from_file(configfile)

    assert c.getpath('app.logging') == os.path.join(
        os.path.dirname(configfile), 'logging.ini')


def test_getpath_no_source_file():
    c = Config({'app.logging': 'logging.ini'})

    assert c.getpath('app.logging') == 'logging.ini'


def test_getpath_default():
    c = Config()

    assert c.getpath('app.logging', None) is None
