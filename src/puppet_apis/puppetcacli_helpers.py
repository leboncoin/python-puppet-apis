# == Helpers
#
# Generate Certificate Signing Request (CSR)
def generate_csr(self, nodename, san=[], ssl_dir=''):
    self.logger.info("---> Generating CSR file for {}".format(nodename))

    if ssl_dir:
        key_file = os.path.join(ssl_dir, "private_keys/{}.pem".format(nodename))
    else:
        key_file = os.path.abspath(self.keyfile)
        key_dir = os.path.dirname(key_file)
        ssl_dir = os.path.join(key_dir, '../')

    csr_file = os.path.join(ssl_dir, 'certificate_request/{}.pem'.format(nodename))

    #Debug output
    self.logger.debug("ssl_dir: {}".format(ssl_dir))
    self.logger.debug("key_file: {}".format(key_file))
    self.logger.debug("csr_file: {}".format(csr_file))

    # Allows you to permanently set values required for CSR
    # To use, comment raw_input and uncomment this section.
    #
    # These options are optionals
    #
    # C  = 'US'
    # ST = 'New York'
    # L  = 'Location'
    # O  = 'Organization'
    # OU = 'Organizational Unit'
    #
    TYPE_RSA = crypto.TYPE_RSA

    req = crypto.X509Req()
    self.logger.info("    * Adding subject Name: {}".format(nodename))
    req.get_subject().CN = nodename

    # Add in extensions
    # added bytearray to string
    # before -> "keyUsage"
    # after  -> b"keyUsage"
    #
    # logger.info("    * Adding constraints")
    # base_constraints = ([
    #     crypto.X509Extension(b"keyUsage", False, b"Digital Signature, Key Encipherment"),
    #     crypto.X509Extension(b"extendedKeyUsage", False, b"TLS Web Server Authentication, TLS Web Client Authentication"),
    #     crypto.X509Extension(b"basicConstraints", False, b"CA:FALSE"),
    # ])
    # x509_extensions = base_constraints

    # Appends SAN to have 'DNS:'
    ss = []
    for i in san:
        self.logger.info("     * Adding Alternate Name: {}".format(i))
        ss.append("DNS: %s" % i)
    ss = ", ".join(ss)
    # If there are SAN entries, append the base_constraints to include them.
    if ss:
        san_constraint = crypto.X509Extension(b"subjectAltName", False, ss)
        #x509_extensions.append(san_constraint)
        req.add_extensions(san_constraint)
    #req.add_extensions(x509_extensions)

    # Utilizes generate_key function to kick off key generation.
    key = self.generate_key(TYPE_RSA, 2048)
    if not self.generate_files(key_file, key):
        return False

    req.set_pubkey(key)
    req.sign(key, "sha256")
    if not self.generate_files(csr_file, req):
        return False

    return True


# Generate Private Key
def generate_key(self, type, bits):
    self.logger.info("---> Generating Key")
    key = crypto.PKey()
    key.generate_key(type, bits)
    return key


# Generate files.
def generate_files(self, mkFile, request):
    self.logger.info("---> Generating file {}".format(mkFile))

    # Make directories if needed
    dir = os.path.dirname(mkFile)
    if not os.path.exists(dir) or not os.path.isdir(dir):
        self.logger.info("     * Creating missing directory {}".format(dir))
        os.makedirs(dir, mode=0o777, exist_ok=False)

    if os.path.exists(mkFile) and os.path.getsize(mkFile) != 0:
        self.logger.info("     * File already exists, skipping ...")
        return True

    else:
        with open(mkFile, "wb") as f:
            if re.match(r'.*request.*', mkFile, flags=re.IGNORECASE):
                self.logger.info("     * Writing certificate_request")
                f.write(crypto.dump_certificate_request(crypto.FILETYPE_PEM, request))

            elif re.match(r'.*private.*', mkFile, flags=re.IGNORECASE):
                self.logger.info("     * Writing private key")
                f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, request))

            elif re.match(r'.*certs.*', mkFile, flags=re.IGNORECASE):
                self.logger.info("     * Writing certificate")
                f.write(request.encode())
                #f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, request))

            else:
                self.logger.error("FAILED, Unknown type of file {}".format(mkFile))
                self.logger.error("FilePath should contain 'request', 'private', 'certs' to follow Puppet CA layout")
                return False

        return True


def submit_csr(self, hostname, ssl_dir=''):
    # Compute cert name
    if not ssl_dir:
        key_file = os.path.abspath(self.keyfile)
        key_dir = os.path.dirname(key_file)
        ssl_dir = os.path.join(key_dir, '../')

    csr_file = os.path.abspath(os.path.join(ssl_dir, "certificate_request/{}.pem".format(hostname)))
    with open(csr_file, "r") as csr:
        self.logger.info("---> Submitting CSR")
        self.logger.info("     * CSR: '{}'".format(csr_file))
        self.logger.info("     * Hostname: '{}'".format(hostname))
        self.logger.info("     * Server: '{}'".format(self.server))

        csr_content = csr.read()
        self.logger.debug("     * CSR Content:'{}'".format(csr_content))

        if not self.puppet_ca_client.submit_csr(hostname, csr_content):
            self.logger.error("FAILED")
            raise PuppetCaCliException

        self.logger.info("SUCCESS")


def download_cert(self, hostname, ssl_dir=''):
    # Compute cert name
    if ssl_dir:
        cert_file = os.path.abspath(os.path.join(ssl_dir, "certs/{}.pem".format(hostname)))
    else:
        cert_dir = os.path.dirname(self.certfile)
        cert_file = os.path.join(cert_dir, "{}.pem".format(hostname))

    # Fetch certificate
    signed_cert = self.puppet_ca_client.get_cert(hostname)
    if self.generate_files(cert_file, signed_cert):
        self.logger.info("     -> {}".format(cert_file))

        delete_csr = self.puppet_ca_client.delete_csr(hostname)
        self.logger.info("     * Delete remote CSR: {}".format(delete_csr))
        return True

    else:
        self.logger.error("FAILED")
        raise PuppetCaCliException


def display_puppetserver_commands(self, hostname):
    self.logger.info("""
    Sign:
    -----
    Go on your puppet-ca and sign the CSR for '{hostname}'

    "puppet cert sign {hostname}"
    or
    "puppet cert --allow-dns-alt-names sign '{hostname}'
    """.format(hostname=hostname))


def display_puppetserver_config(self, hostname):
    self.logger.info("""
    Puppet Server Config:
    -----
    And add this snippet to your server config "/etc/puppetlabs/puppetserver/conf.d/auth.conf"

    ```
    authorization: {{
        version: 1
        rules: [
            {{
                "allow": [
                    "{hostname}"
                ],
                "match-request": {{
                    "method": [
                        "delete",
                        "get",
                        "put"
                    ],
                    "path": "^/puppet-ca/v1/certificate_status/",
                    "query-params": {{}},
                    "type": "regex"
                }},
                "name": "Puppet CA Admin users",
                "sort-order": 200
            }}
    ```
    """.format(hostname=hostname))
