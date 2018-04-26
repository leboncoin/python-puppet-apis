"""
DOC
"""
import sys
from .puppetbase import PuppetBaseAPI
from requests.exceptions import (
    ConnectionError,
)


class PuppetCaException(Exception):
    sys.tracebacklimit = 0
    pass


class PuppetCa(PuppetBaseAPI):
    """
    PuppetCA endpoint exposing methodes for node decommission.
    """
    def __init__(self, server,
                 scheme='https', port=8140,
                 ca_cert_path='', client_cert_path='', client_key_path=''):
        super().__init__(
            server=server,
            port=port,
            scheme=scheme,
            ca_cert_path=ca_cert_path,
            client_cert_path=client_cert_path,
            client_key_path=client_key_path
        )
        self.uri = '{scheme}://{server}:{port}'.format(
            scheme=self.scheme,
            server=self.server,
            port=self.port
        )


    # === Certifiate Status
    #
    # https://puppet.com/docs/puppet/4.10/http_api/http_certificate_status.html
    #
    def delete(self, node_fqdn):
        """
        Delete a node certificate
        """
        url = '{}/puppet-ca/v1/certificate_status/{}'.format(self.uri, node_fqdn)
        self.logger.debug("{}: URL={}".format(__name__, url))

        response = self.session.delete(url)
        return bool(response.status_code in [200, 202, 204,])


    def revoke(self, node_fqdn):
        """
        Revoke a node certificate
        """
        url = '{}/puppet-ca/v1/certificate_status/{}'.format(self.uri, node_fqdn)
        self.logger.debug("{}: URL={}".format(__name__, url))

        headers = {
            'Content-Type': 'application/json'
        }
        data = '{"desired_state":"revoked"}'

        response = self.session.put(
            url,
            headers=headers, data=data
        )
        return bool(response.status_code in [200, 204,])


    def sign(self, node_fqdn):
        """
        Sign a node certificate request
        """
        url = '{}/puppet-ca/v1/certificate_status/{}'.format(self.uri, node_fqdn)
        self.logger.debug("{}: URL={}".format(__name__, url))

        headers = {
            'Content-Type': 'application/json'
        }
        data = '{"desired_state":"signed"}'

        response = self.session.put(
            url,
            headers=headers, data=data
        )
        return bool(response.status_code in [200, 204,])


    def status(self, node_fqdn):
        """
        Get the status of a node certificate
        """
        url = '{}/puppet-ca/v1/certificate_status/{}'.format(self.uri, node_fqdn)
        self.logger.debug("{}: URL={}".format(__name__, url))

        try:
            response = self.session.get(url, verify=False)
        except ConnectionError as e:
            self.logger.error("{}: {}".format(__name__, e))
            raise PuppetCaException

        if response.status_code == 200:
            return response.json()
        return {}


    # === Certifiate
    #
    # https://puppet.com/docs/puppet/4.10/http_api/http_certificate.html
    #
    def get_cert(self, node_fqdn):
        """
        Get a certificate
        """
        url = '{}/puppet-ca/v1/certificate/{}'.format(self.uri, node_fqdn)
        self.logger.debug("{}: URL={}".format(__name__, url))

        response = self.session.get(url, verify=False)

        # The returned certificate is always in the .pem format.
        # Other messages are plain text
        return response.text


    # === Certifiate Requests
    #
    # https://puppet.com/docs/puppet/4.10/http_api/http_certificate_request.html
    #
    def get_csr(self, node_fqdn):
        """
        Get a certificate request
        """
        url = '{}/puppet-ca/v1/certificate_request/{}'.format(self.uri, node_fqdn)
        self.logger.debug("{}: URL={}".format(__name__, url))

        response = self.session.get(url, verify=False)

        # The returned certificate is always in the .pem format.
        # Other messages are plain text
        return response.text


    def submit_csr(self, node_fqdn, csr):
        """
        Submit a certificate request
        """
        url = '{}/puppet-ca/v1/certificate_request/{}'.format(self.uri, node_fqdn)
        self.logger.debug("{}: URL={}".format(__name__, url))

        headers = {
            'Content-Type': 'text/plain'
        }

        response = self.session.put(
            url,
            headers=headers, data=csr
        )
        self.logger.debug("{}: response.code = {}".format(__name__, response.status_code))
        self.logger.debug("{}: response.text = {}".format(__name__, response.text))
        return bool(response.status_code in [200, 204,])


    def delete_csr(self, node_fqdn):
        """
        Delete a certificate request
        """
        url = '{}/puppet-ca/v1/certificate_request/{}'.format(self.uri, node_fqdn)
        self.logger.debug("{}: URL={}".format(__name__, url))

        response = self.session.delete(url, verify=False)

        # The returned certificate is always in the .pem format.
        # Other messages are plain text
        return response.text
