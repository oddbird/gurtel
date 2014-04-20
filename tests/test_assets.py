from cStringIO import StringIO
import os

import pytest

from gurtel import assets


@pytest.fixture
def static_dir(testapp_base_dir):
    return os.path.join(testapp_base_dir, 'static')


@pytest.fixture
def handler(static_dir):
    return assets.AssetHandler(static_dir, '/static/', minify=False)


class TestAssetHandler(object):
    def test_assets_env_config(self, handler, static_dir):
        """Instantiates and configures a webassets Environment."""
        assert handler.directory == handler.assets_env.directory == static_dir
        assert handler.url == handler.assets_env.url == '/static/'
        assert handler.assets_env.config['debug']
        assert 'css' in handler.assets_env


def test_rcssmin(monkeypatch):
    """rcssmin filter calls cssmin on the input and writes result to output."""
    # our fake (and ineffective) minifier doubles the input string
    monkeypatch.setattr(assets, 'cssmin', lambda i: i + i)
    _in = StringIO('foo')
    out = StringIO()

    rcssmin = assets.RCSSMin()

    rcssmin.output(_in, out)

    out.seek(0)
    assert out.read() == 'foofoo'


def test_get_bundles(tmpdir):
    """Returns bundles from given YAML file."""
    yaml_file = os.path.join(str(tmpdir), 'bundles.yml')
    with open(yaml_file, 'w') as fh:
        fh.write('css:\n  output: out.css\n  contents:\n    - in.css')

    bundles = assets.get_bundles(yaml_file)

    assert len(bundles) == 1
    assert bundles['css'].output == 'out.css'
    assert bundles['css'].contents == ('in.css',)
