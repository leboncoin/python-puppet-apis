import json

from time import altzone, localtime, timezone
from datetime import datetime, timedelta, timezone as dt_timezone

from .puppetbase import PuppetBaseAPI


class PuppetDb(PuppetBaseAPI):
    """
    A PuppetDB endpoint exposing methodes for node decommission.
    """
    def __init__(self, server,
                 scheme='http', port=8080,
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


    def status(self, node_fqdn):
        """
        Get the status of a node certificate
        """
        url = '{}/pdb/query/v4/nodes/{}'.format(self.uri, node_fqdn)
        self.logger.debug("{}: URL={}".format(__name__, url))

        response = self.session.get(url, verify=False)
        return response.json()


    def deactivate(self, node_fqdn):
        """
        Deactivate a node
        """
        url = '{}/pdb/cmd/v1'.format(self.uri)
        self.logger.debug("{}: URL={}".format(__name__, url))

        headers = {
            'Content-Type': 'application/json'
        }

        # calculate the offset taking into account daylight saving time
        utc_offset_sec = altzone if localtime().tm_isdst else timezone
        offset = timedelta(seconds=utc_offset_sec)
        tzinfo = dt_timezone(offset=offset)
        tstamp = datetime.now().replace(tzinfo=tzinfo, microsecond=0).isoformat()
        self.logger.debug("{}: producer_timestamp={}".format(__name__, tstamp))

        data = {
          "command": "deactivate node",
          "version": 3,
          "payload": {
              "certname": node_fqdn,
              "producer_timestamp": tstamp
          }
        }

        response = self.session.post(
            url,
            headers=headers, data=json.dumps(data)
        )
        return response.json()
