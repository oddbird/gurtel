from ConfigParser import RawConfigParser
import os


NOT_PROVIDED = object()


class Config(object):
    """Dictionary-like configuration holder."""
    def __init__(self, data=None):
        self.data = {}
        if data is not None:
            self.data.update(data)
        # Maps keys to their source file (if any)
        self.sourcemap = {}

    def read_from_file(self, conf_file):
        """
        Read config from an ini-style config file.

        Section and key names are dot-joined into a single flat config
        namespace; e.g. this config file::

            [section]
            foo = bar

        results in a config key ``section.foo`` with value ``"bar"``.

        """
        parser = RawConfigParser()
        with open(conf_file) as f:
            parser.readfp(f)

        for section in parser.sections():
            for k, v in parser.items(section):
                key = '.'.join([section, k])
                self.data[key] = v
                self.sourcemap[key] = conf_file

        return self

    def read_from_env(self, prefix, env=None):
        """
        Read config from given env dict (``os.environ`` by default).

        Only env vars beginning with ``prefix`` are considered. Env vars are
        lowercased and "__" (double underscore) replaced with "." (period) in
        order to form a config key. Thus if ``prefix`` is "CONFIG_", the env
        var "CONFIG_DATABASE__URI" would become the config key "database.uri".

        """
        if env is None:
            env = os.environ

        for k, v in env.items():
            if k.startswith(prefix):
                k = k[len(prefix):].lower().replace('__', '.')
                self.data[k] = v
                self.sourcemap[k] = None

        return self

    def update(self, d):
        """Update config from a dict."""
        self.data.update(d)
        for k in d:
            self.sourcemap[k] = None

    def copy(self):
        """Return a copy of this config."""
        c = self.__class__(self.data)
        c.sourcemap = self.sourcemap.copy()

        return c

    def get(self, key, default=None):
        """Proxy .get() to config dict."""
        return self.data.get(key, default)

    def __getitem__(self, key):
        """Proxy __getitem__ to config dict."""
        return self.data[key]

    def __contains__(self, key):
        """Proxy __contains__ to config dict."""
        return key in self.data

    def keys(self):
        """Proxy keys() to config dict."""
        return self.data.keys()

    truthy = frozenset({'y', 'yes', 't', 'true', '1', 'on', True})
    falsy = frozenset({'n', 'no', 'f', 'false', '0', 'off', False})

    def getbool(self, key, default=NOT_PROVIDED):
        """
        Get a boolean config value.

        If lower-cased value is in ``{'y', 'yes', 't', 'true', '1', 'on'}``,
        return ``True``. If lower-cased value is in ``{'n', 'no', 'f', 'false',
        '0', 'off'}``, return ``False``. Else raise ``ValueError``.

        """
        try:
            original = self[key]
        except KeyError:
            if default is NOT_PROVIDED:
                raise
            val = original = default
        else:
            val = original.lower()

        if val in self.truthy:
            return True
        elif val in self.falsy:
            return False
        else:
            raise ValueError(
                "Value %r for config key %r is not a boolean."
                % (original, key)
                )

    def getpath(self, key, default=NOT_PROVIDED):
        """
        Get a config value as a path relative to its source file.

        If the config did not come from a file, returns the path unchanged.

        """
        try:
            val = self[key]
        except KeyError:
            if default is NOT_PROVIDED:
                raise
            return default

        source = self.sourcemap.get(key)
        if source is not None:
            val = os.path.join(os.path.dirname(source), val)

        return val
