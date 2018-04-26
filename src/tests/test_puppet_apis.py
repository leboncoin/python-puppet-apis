import os
import pytest
import requests
from requests.exceptions import (
    ConnectionError,
)

from puppet_apis import PuppetCa, PuppetDb


# == Config
#
test_dir = os.path.dirname(os.path.realpath(__file__))
CA_CONFIG = {
    "ca_cert": "{}/../../tests/docker-compose/puppet_apis/ssl/certs/ca.pem".format(test_dir),
    "client_cert": "{}/../../tests/docker-compose/puppet_apis/ssl/certs/admin1.mydomain.com.pem".format(test_dir),
    "client_key": "{}/../../tests/docker-compose/puppet_apis/ssl/private_keys/admin1.mydomain.com.pem".format(test_dir)
}

NODE1='node01.mydomain.com'
NODE2='node02.mydomain.com'
NODE3='node03.mydomain.com'


# == Helpers
#
def is_responsive(url):
    """Check if something responds to ``url``."""
    try:
        response = requests.get(url, verify=False)
        print(response.status_code)
        if response.status_code == 200:
            return True
    except ConnectionError:
        return False


def log_pytest(message):
    print ("====> PYTEST: {}".format(message))


def run_puppet_agent(nodename):
    log_pytest("Run Puppet agent Node: {}".format(nodename))
    return os.system("""
    docker run --rm --net puppetapis_default\
               puppet/puppet-agent-debian agent \
                    --onetime --no-daemonize \
                    --certname={};
    """.format(nodename))


# == Fixtures
#
@pytest.fixture(scope='session')
def docker_compose_project_name():
    return 'puppetapis'


@pytest.fixture(scope='session')
def puppetca_client(docker_ip, docker_services):
    return PuppetCa(
        scheme='https',
        server=docker_ip,
        port=docker_services.port_for('puppet', 8140),
        client_cert_path=CA_CONFIG['client_cert'],
        client_key_path=CA_CONFIG['client_key']
    )


@pytest.fixture(scope='session')
def puppetdb_client(docker_ip, docker_services):
    return PuppetDb(
        scheme='http',
        server=docker_ip,
        port=docker_services.port_for('puppetdb', 8080),
        client_cert_path=CA_CONFIG['client_cert'],
        client_key_path=CA_CONFIG['client_key']
    )


# == Tests
#
# Waiter before testing
#
def test_puppetserver_alive(docker_ip, docker_services):
     """Ensure that "puppetserver" is up and responsive."""
     url = 'https://{host}:{port}{path}'.format(
        host=docker_ip,
        port=docker_services.port_for('puppet', 8140),
        path='/status/v1/services'
     )
     docker_services.wait_until_responsive(
       timeout=90.0, pause=0.1,
       check=lambda: is_responsive(url)
     )


def test_puppetdb_alive(docker_ip, docker_services):
     """Ensure that "PuppetDB" is up and responsive."""
     url = 'http://{host}:{port}{path}'.format(
        host=docker_ip,
        port=docker_services.port_for('puppetdb', 8080),
        path='/status/v1/services/puppetdb-status'
     )
     docker_services.wait_until_responsive(
       timeout=90.0, pause=0.1,
       check=lambda: is_responsive(url)
     )


def test_puppetca_run_puppet_agents_node2():
    exit_code = run_puppet_agent(NODE2)
    assert exit_code == 0


def test_puppetca_run_puppet_agents_node3():
    exit_code = run_puppet_agent(NODE3)
    assert exit_code == 0


# == PuppetCA API:
#
# === Node does NOT exist
#
def test_puppetca_status_node1_does_not_exist(puppetca_client):
    response = puppetca_client.status(NODE1)
    assert response == {}


def test_puppetca_revoke_node1_does_not_exist(puppetca_client):
    response = puppetca_client.revoke(NODE1)
    assert response == False


def test_puppetca_delete_node1_does_not_exist(puppetca_client):
    response = puppetca_client.delete(NODE1)
    assert response == False


# === Node exists
#
def test_puppetca_status_node2_exist(puppetca_client):
    response = puppetca_client.status(NODE2)
    assert 'state' in response
    assert response['state'] == 'signed'


def test_puppetca_delete_node2_exist_not_revoked(puppetca_client):
    # https://puppet.com/docs/puppet/5.4/http_api/http_certificate_status.html#delete
    response = puppetca_client.delete(NODE2)
    assert response == True

    response = puppetca_client.status(NODE2)
    assert response == {}


# === Node exists
#
def test_puppetca_revoke_node3_exist(puppetca_client):
    response = puppetca_client.revoke(NODE3)
    assert response == True

    response = puppetca_client.status(NODE3)
    assert 'state' in response
    assert response['state'] == 'revoked'


def test_puppetca_delete_node3_exist(puppetca_client):
    response = puppetca_client.delete(NODE3)
    assert response == True

    response = puppetca_client.status(NODE3)
    assert response == {}


# == PuppetDB API:
#
# - https://puppet.com/docs/puppetdb/4.4/api/status/v1/status.html
# - https://puppet.com/docs/puppetdb/4.4/api/command/v1/commands.html#deactivate-node-version-3
#
def test_puppetdb_status_node1_does_not_exist(puppetdb_client):
    response = puppetdb_client.status(NODE1)
    assert 'error' in response


def test_puppetdb_deactivate_node1_does_not_exist(puppetdb_client):
    response = puppetdb_client.deactivate(NODE1)
    assert 'uuid' in response


def test_puppetdb_status_node2_exist(puppetdb_client):
    response = puppetdb_client.status(NODE2)
    assert 'deactivated' in response
    assert response['deactivated'] is None


def test_puppetdb_deactivate_node2_exist(puppetdb_client):
    response = puppetdb_client.deactivate(NODE2)
    assert 'uuid' in response

    response = puppetdb_client.status(NODE2)
    assert 'deactivated' in response
    assert response['deactivated'] is not None
