import os

import pytest



@pytest.fixture
def configfile(request, tmpdir):
    if 'configfile_contents' in request.keywords:
        contents = request.keywords['configfile_contents'].args[0]
    else:
        contents = ''

    fn = os.path.join(str(tmpdir), 'config.ini')
    with open(fn, 'w') as fh:
        fh.write(contents)

    return fn
