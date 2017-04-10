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

def error(message):
    print message
    sys.exit(-1)

if __name__ == "__main__":

    config = Config()
    dns = DNS(config.get("domain").get("dns"))
    db = Database(config.get("database"))
    validations = Validations(db, config.get("domain"))

    parser = argparse.ArgumentParser(description="Manage RED redirections with command-line utility")
    parser.add_argument("action", choices=['add', 'del', 'list', 'check'], help="Action")
    parser.add_argument("domain", help="Domain name", nargs='?')
    parser.add_argument("url", nargs='?', help="Destination URL")
    args = parser.parse_args()

    domain = args.domain
    action = args.action

    if action == 'list':
        for red in db.get_redirections():
            print "%(date_added)s %(domain)s -> %(url)s" % red
    elif action == 'add':
        url = args.url

        if not url:
            error("You must define the destionation rediretion URL")

        result = validations.check_redirection_can_be_added(domain, url)
        if result.get("status") == 500:
            error(result.get("message"))
        db.add_redirection({ "domain": domain, "url": url})
    elif action == 'del':
        db.del_redirection_by_domain(domain)
    elif action == 'check':
        for redirection in db.get_redirections():
            domain_result = validations.check_domain_exists(redirection.get('domain'))            
            redirection_result = validations.check_redirection_status(redirection)
            print redirection.get('domain')
            print domain_result
            print redirection_result
            if redirection_result.get("status") != 200:
                db.update_status(redirection.get('id'), False, result.get("message"))
            elif domain_result == False:
                db.update_status(redirection.get('id'), False, 'Domain does not exist in DNS')
            else:                                
                db.update_status(redirection.get('id'), True, '')
