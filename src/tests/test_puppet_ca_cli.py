import os
import pytest

from helpers.utils import is_responsive, log_pytest, run_puppet_agent
from puppet_apis import PuppetCa
from puppet_apis import PuppetCaCli


# == Config
#
test_root_dir = os.path.dirname(os.path.realpath(__file__))
clientname='admin2.mydomain.com'
NODE4='node04.mydomain.com'



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
        port=docker_services.port_for('puppet', 8140)
    )


@pytest.fixture(scope='session')
def puppetca_cli_config(docker_ip, docker_services):
    return {
        'puppetserver': {
            'server': docker_ip,
            'port': docker_services.port_for('puppet', 8140),
        },
        'ssl': {
            'client_name': clientname,
            'client_cert': '{}/../../tests/docker-compose/puppetca_cli/ssl/certs/{}.pem'.format(test_root_dir, clientname),
            'client_key': '{}/../../tests/docker-compose/puppetca_cli/ssl/private_keys/{}.pem'.format(test_root_dir, clientname)
        }
    }


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


# Populating the stack
#
def test_puppetca_run_puppet_agents_node():
    assert run_puppet_agent(NODE4) == 0


# == PuppetCA CLI:
#
# === User actions: Creating certificate
#
def test_puppetca_status_empty_for_admin(puppetca_client):
    """Testing puppetca status with module function"""
    response = puppetca_client.status(clientname)
    assert response == {}


def test_puppetca_cli_init(puppetca_cli_config):
    """Testing initialisation of puppet-ca-cli"""
    config = puppetca_cli_config
    cli = PuppetCaCli(config)

    assert cli.init(hostname=clientname, san='')
    assert os.path.exists(config['ssl']['client_key'])


def test_puppetca_cli_install_cert(puppetca_cli_config):
    config = puppetca_cli_config
    cli = PuppetCaCli(config)

    assert cli.install(hostname=clientname)
    assert os.path.exists(config['ssl']['client_cert'])


def test_puppetca_cli_status_success(puppetca_cli_config, puppetca_client):
    config = puppetca_cli_config
    cli = PuppetCaCli(config)

    status = cli.status(hostname=NODE4)
    assert status

    puppetca_response = puppetca_client.status(NODE4)
    assert puppetca_response == status


# === Admin actions: signing, revoking and deleting certificate
#
def test_puppetca_cli_revoke(puppetca_cli_config, puppetca_client):
    config = puppetca_cli_config
    cli = PuppetCaCli(config)

    assert cli.revoke(hostname=NODE4) == True

    status = cli.status(hostname=NODE4)
    assert 'state' in status
    assert status['state'] == 'revoked'

    puppetca_response = puppetca_client.status(NODE4)
    assert puppetca_response['state'] == status['state']


def test_puppetca_cli_delete(puppetca_cli_config, puppetca_client):
    config = puppetca_cli_config
    cli = PuppetCaCli(config)

    assert cli.delete(hostname=NODE4) == True

    status = cli.status(hostname=NODE4)
    assert status == False

    puppetca_response = puppetca_client.status(NODE4)
    assert puppetca_response == {}


# def test_puppetca_cli_sign(puppetca_cli_config):
#     config = puppetca_cli_config
#     cli = PuppetCaCli(config)
#
#     assert cli.sign(hostname=NODE4)
#
#     puppetca_response = puppetca_client.status(clientname)
#     assert 'state' in puppetca_response
#     assert puppetca_response['state'] == 'signed'
#
