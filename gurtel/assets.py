from rcssmin import cssmin
from webassets.filter import register_filter, Filter
from webassets.loaders import YAMLLoader


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
