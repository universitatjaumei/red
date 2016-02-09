#!/usr/bin/python2

import argparse
import os
import sys
import re
import os
from commons.config import Config
from commons.validations import Validations
from commons.database import Database
from commons.dns import DNS

if __name__ == "__main__":

    config = Config()
    dns = DNS(config.get("dns"))
    db = Database(config.get("database"))
    validations = Validations(db)

    parser = argparse.ArgumentParser(description="Manage RED redirections with command-line utility")
    parser.add_argument("add", help="app.properties file location")
    parser.add_argument("domain", help="Domain name")
    parser.add_argument("url", help="Destination URL")
    args = parser.parse_args()

    domain = args.domain
    url = args.url

    def error(message):
        print message
        sys.exit(-1)

    result = validations.check_redirection_can_be_added(domain, url)

    if result.get("status") == 500:
        error(result.get("message"))

    db.add_redirection({ "hostname": domain, "url": url})
