import yaml
import os
import socket
from commons.validations import Validations
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
              INSERT INTO GEI_DNS_MANUAL(NOM_BASE, ALIAS) VALUES
                ('redirecciones-557693514.eu-west-1.elb.amazonaws.com',
                 '%s'
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

    def check_domain_exists(self, domain):
        try:
            socket.gethostbyname(domain)
            return True
        except socket.gaierror:
            return False

    def add_domain(self, domain):
        if self.check_domain_exists(domain):
            return True

        if self.db:
            return self.db.add_domain(domain)

        return True

    def delete_domain(self, domain):
        #if not self.check_domain_exists(domain):
        #    return False

        if self.db:
            self.db.delete_domain(domain)

        return True
