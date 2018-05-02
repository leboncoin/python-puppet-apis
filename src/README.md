# python-puppet-apis


A python module for administrative tasks on PuppetCa and PuppetDb

-> Provides also a CLI script to bootstrap SSL certs like the `puppet-agent`


[![Build Status](https://travis-ci.org/leboncoin/python-puppet-apis.svg?branch=master)](https://travis-ci.org/leboncoin/python-puppet-apis)


<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Usage in code](#usage-in-code)
  - [Install](#install)
  - [Setup](#setup)
  - [Use](#use)
- [CLI](#cli)
- [PuppetSever Auth.conf](#puppetsever-authconf)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->



## Usage in code

### Install

```
git clone https://github.com/leboncoin/python-puppet-apis/
cd python-puppet-apis/src/
pip install -e .
```


### Setup

On your puppet master
```
$ puppet cert generate --dns-alt-names YOUR_CLIENT_FQDN
$ puppet cert --allow-dns-alt-names sign YOUR_CLIENT_FQDN
```

Get the files

```
puppet-apis_client/ssl/
├── certs/
│   ├── ca.pem
│   └── YOUR_CLIENT_FQDN.pem
├── private_keys/
│   └── YOUR_CLIENT_FQDN.pem
└── public_keys/
    └── YOUR_CLIENT_FQDN.pem
```


### Use

```
>>> import puppet_apis
>>> puppetca = puppet_apis.PuppetCa(
    server='puppet-ca.yourdomain.com',
    port=8140,
    client_cert_path='PATH_TO/puppet-apis_client/ssl/certs/YOUR_CLIENT_FQDN.pem',
    client_key_path='PATH_TO/puppet-apis_client/ssl/private_keys/YOUR_CLIENT_FQDN.pem'
    )

>>> puppetca.status('YOUR_CLIENT_FQDN')
{'name': 'YOUR_CLIENT_FQDN', 'state': 'signed', 'dns_alt_names': ['DNS:lorie', 'DNS:YOUR_CLIENT_FQDN'], 'fingerprint': '4D:B2:AD:A2:80:07:15:88:5F:46:0A:A3:82:43:A1:CE:60:03:AF:3B:15:31:5A:EF:6A:97:10:26:7E:CE:1E:16', 'fingerprints': {'SHA1': '37:82:48:1F:D2:CD:E4:1B:78:50:D7:14:0E:66:16:99:1B:C0:07:16', 'SHA256': '4D:B2:AD:A2:80:07:15:88:5F:46:0A:A3:82:43:A1:CE:60:03:AF:3B:15:31:5A:EF:6A:97:10:26:7E:CE:1E:16', 'SHA512': 'EC:1D:66:79:6D:CD:57:68:C6:8F:82:49:09:76:71:51:E3:5F:45:F6:3B:98:36:2F:F1:C6:A2:D3:DA:17:7A:9C:81:DE:BA:16:BD:F2:6C:0D:89:0C:CB:6C:1A:33:69:8A:17:F0:4C:4A:B9:84:02:D6:AB:2E:05:97:16:54:6A:68', 'default': '4D:B2:AD:A2:80:07:15:88:5F:46:0A:A3:82:43:A1:CE:60:03:AF:3B:15:31:5A:EF:6A:97:10:26:7E:CE:1E:16'}}

>>> puppetca.delete('YOUR_CLIENT_FQDN')
True

>>> puppetca.status('YOUR_CLIENT_FQDN')
{}
```



## CLI

Available docker wrapper in [`./bin/`](./bin/)

```
$ puppet-ca-cli -h

usage: puppet-ca-cli [-h] [--server SERVER] [-s [SAN [SAN ...]]] command name

positional arguments:
  command               Command: init, install, status
  name                  Provide the FQDN

optional arguments:
  -h, --help            show this help message and exit
  --server SERVER       Puppet CA server address
  -s [SAN [SAN ...]], --san [SAN [SAN ...]]
                        SANS
```


## PuppetSever Auth.conf

An example can be found in [tests/docker-compose/puppetserver/conf/auth.conf](tests/docker-compose/puppetserver/conf/auth.conf)
