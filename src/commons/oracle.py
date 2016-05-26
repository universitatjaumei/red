import yaml
import os
import socket
import time
import xmlrpclib
from validations import Validations
from sqlalchemy import Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

class OracleDatabase:
    def __init__(self, oracle_conn):
        self.engine = create_engine(oracle_conn, echo=True)

    def check_exists_domain(self, domain):
        p = self.engine.execute("""
          SELECT count(*) as count FROM GEI_DNS_MANUAL WHERE
            alias='%s'
        """ % domain)

        return p.fetchone()[0] > 0

    def add_domain(self, domain):
        if not self.check_exists_domain(domain):
            p = self.engine.execute("""
              INSERT INTO GEI_DNS_MANUAL(NOM_BASE, ALIAS, TIPO) VALUES
                ('redirecciones-557693514.eu-west-1.elb.amazonaws.com',
                 '%s', 'CNAME'
                )
            """ % domain)
            return True
        return False

    def delete_domain(self, domain):
        if self.check_exists_domain(domain):
            p = self.engine.execute("""
              DELETE from GEI_DNS_MANUAL WHERE
                ALIAS='%s'
            """ % domain);

            return True
        return False


class DNS:
    def __init__(self, config):
        if config.get("db_conn"):
            self.db = OracleDatabase(config.get("db_conn"))
        else:
            self.db = None

        if config.get("dns"):
            self.xmlrpc_server = config.get("dns").get("xmlrpc_server")
            self.xmlrpc_method = config.get("dns").get("xmlrpc_method")
        else:
            self.xmlrpc_server = None
            self.xmlrpc_method = None

    def check_domain_exists(self, domain):
        try:
            socket.gethostbyname(domain)
            return True
        except socket.gaierror:
            return False

    def add_domain(self, domain):
        if self.check_domain_exists(domain):
            return False

        if self.db:
            return self.db.add_domain(domain)

        return True

    def delete_domain(self, domain):
        #if not self.check_domain_exists(domain):
        #    return False

        if self.db:
            self.db.delete_domain(domain)

        return True

    def check_lock(self):
        if os.path.isfile("/tmp/red_dns_lock"):
            if time.time() - os.path.getmtime("/tmp/red_dns_lock") < 60:
                return False
            os.remove("/tmp/red_dns_lock")

        open('/tmp/red_dns_lock', 'w+')
        return True

    def xmlrpc_dns_generate(self):
        server = xmlrpclib.Server(self.xmlrpc_server);
        xmlrpc_method = getattr(server, self.xmlrpc_method)
        xmlrpc_response = xmlrpc_method()
        if xmlrpc_response:
            status = xmlrpc_response[0]
            if status == 0:
                return { "status": 200, "message": "DNS generated successfully." }

        return { "status": 500, "message": "Error calling the remote DNS synchronization." }


    def generate_zone(self):
        if not self.check_lock():
            return  { "status": 500, "message": "Please wait at least 1 minute to regenerate the DNS again." }

        return self.xmlrpc_dns_generate()

if __name__ == "__main__":
    from config import Config
    config = Config()
    dns = DNS(config.get("domain"))
    print dns.generate_zone()
