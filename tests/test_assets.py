from cStringIO import StringIO
import os

from gurtel import assets



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
