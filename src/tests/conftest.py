# Conftest.py: Sharing fixtures functions
#
# https://docs.pytest.org/en/latest/fixture.html#conftest-py-sharing-fixture-functions
#
import os
import pytest


@pytest.fixture(scope='session')
def docker_compose_file(pytestconfig):
    return os.path.join(
        str(pytestconfig.rootdir),
        '../tests',
        'docker-compose.yml'
    )
