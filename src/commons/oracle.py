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

if __name__ == "__main__":
    from config import Config
    config = Config()
    dns = DNS(config.get("domain"))
    print dns.generate_zone()
