import logging

from certifi import where as certifi_where
from requests import Session, exceptions


class PuppetBaseAPI:
    """
    Base Puppet* HTTP API client
    """
    def __init__(self, scheme, server, port,
                 ca_cert_path='', client_cert_path='', client_key_path=''):
        # Flask App
        self.logger = logging.getLogger()
        #logging.basicConfig(filename='puppet.log',level=logging.DEBUG)
        #self.logger = logging

        # Puppet Host
        self.scheme = scheme
        self.server = server
        self.port = port

        # Client side certificates
        self.ca_cert_path = ca_cert_path

        #TODO: --tlsv1 \
        self.session = Session()
        self.session.headers.update({"Accept": "application/json"})
        self.session.verify = False

        if client_cert_path and client_key_path:
            self.session.cert = (client_cert_path, client_key_path)

        # # PuppetServer CAcert
        # try:
        #     self.logger.debug("{}: Checking connection to {}...".format(__name__, server))
        #
        #     #TODO: Enable SSL verification
        #     self.session.get('{}://{}:{}'.format(scheme, server, port), verify=False)
        #     self.logger.debug("{}: Connection to {} OK.".format(__name__, server))
        #
        # except exceptions.SSLError:
        #     self.logger.debug("{}: SSL Error. setting Verify to FALSE".format(__name__))
        #     self.session.verify = False

            #self.logger.debug("{}: SSL Error. Adding custom certs to Certifi store...".format(__name__))
            # cafile = certifi_where()
            # self.logger.debug("{}: Certs found: {}".format(__name__, cafile))
            #
            # self.logger.debug("{}: Reading CA Certs from Puppet".format(__name__))
            # with open(ca_cert_path, 'rb') as infile:
            #     customca = infile.read()
            #
            # self.logger.debug("{}: Adding CA Certs from Puppet to Certifi store".format(__name__))
            # with open(cafile, 'ab') as outfile:
            #     outfile.write(customca)
            #
            # self.logger.debug("{}: Custom cert sucessfully added".format(__name__))
