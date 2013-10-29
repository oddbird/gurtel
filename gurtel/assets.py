import os

from rcssmin import cssmin
from webassets import Environment
from webassets.filter import register_filter, Filter
from webassets.loaders import YAMLLoader


class AssetHandler(object):
    """
    Encapsulates handling of static assets for a Gurtel app.

    Given a static assets directory ``static_dir`` and a static assets URL
    ``static_url`` (and a ``minify`` boolean defaulting to ``True``),
    configures a webassets Environment accordingly and registers all static
    asset bundles described in ``static_dir/bundles.yml``.

    """
    def __init__(self, static_dir, static_url, minify=True):
        self.assets_env = Environment(
            static_dir,
            static_url,
            debug=not minify,
            )
        self.assets_env.register(
            get_bundles(os.path.join(static_dir, 'bundles.yml')))



class RCSSMin(Filter):
    """Minifies CSS using the rCSSmin library."""

    name = 'rcssmin'

    def output(self, _in, out, **kw):
        out.write(cssmin(_in.read()))


register_filter(RCSSMin)


def get_bundles(yaml_file):
    """Load bundle definitions from given YAML file."""
    loader = YAMLLoader(yaml_file)

    return loader.load_bundles()
