# Conftest.py: Sharing fixtures functions
#
# https://docs.pytest.org/en/latest/fixture.html#conftest-py-sharing-fixture-functions
#
import os
import pytest
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))

@pytest.fixture(scope='session')
def docker_compose_file(pytestconfig):
    return os.path.join(
        str(pytestconfig.rootdir),
        '../tests',
        'docker-compose.yml'
    )
