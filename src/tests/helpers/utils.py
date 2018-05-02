import os
import requests
from requests.exceptions import (
    ConnectionError,
)

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
