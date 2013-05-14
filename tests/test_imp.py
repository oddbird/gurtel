from gurtel import imp


something = object()


def test_import_from_module():
    """Can import an object from a module given a dotted path."""
    assert imp.import_from_dotted_path(
        'tests.test_imp.something') is something
