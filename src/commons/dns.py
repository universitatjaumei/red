import yaml
import os
from oracle import OracleDatabase
from commons.validations import Validations
import socket

class DNS:
    def __init__(self, config):
        self.oracle = OracleDatabase(config.get("oracle_conn"))

    def check_domain_exists(self, domain):
        try:
            socket.gethostbyname(domain)
            return True
        except socket.gaierror:
            return False

    def add_domain(self, domain):
        if self.check_domain_exists(domain):
            return False

        return self.oracle.add_domain(domain)

    def delete_domain(self, domain):
        #if not self.check_domain_exists(domain):
        #    return False

        return self.oracle.delete_domain(domain)
