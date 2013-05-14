from importlib import import_module


def import_from_dotted_path(dotted_path):
    mod_path, attr = dotted_path.rsplit('.', 1)
    module = import_module(mod_path)
    return getattr(module, attr)
