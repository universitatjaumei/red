from rfc3987 import parse
import socket
import re
import urllib2

class Validations:
    def __init__(self, db, domain_config):
        self.db = db
        self.local_domain = domain_config.get('name', None)

    def check_valid_domain(self, domain):
        pattern = re.compile(
            r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
            r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
            r'([a-zA-Z0-9][-_.a-zA-Z0-9]{1,61}[a-zA-Z0-9]))\.'
            r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$'
        )

        return pattern.search(domain)

    def check_destination_url(self, url):
        try:
            o = parse(url)
            return o.get('scheme') and o.get('authority')
        except ValueError:
            return False

    def check_domain_exists(self, domain):
        try:
            socket.gethostbyname(domain)
            return True
        except socket.gaierror:
            return False

    def check_local_domain(self, domain):
        pattern = re.compile(
            r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
            r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
            r'([a-zA-Z0-9][-_.a-zA-Z0-9]{1,61}[a-zA-Z0-9]))\.'
            r'%s$' % self.local_domain
        )

        return pattern.search(domain)

    def check_url_valid_status_code(self, url):
        try:
            urllib2.urlopen(url)
            return True
        except urllib2.HTTPError, e:
            return False
        except urllib2.URLError, e:
            return False

    def is_duplicated_in_db(self, domain):
        return self.db.get_redirection_by_domain(domain) != None

    def check_redirection_can_be_added(self, domain, url):
        if not self.check_valid_domain(domain):
            return { "status": 500, "message": "Invalid domain" }

        if not self.check_destination_url(url):
            return { "status": 500, "message": "Invalid redirection url" }

        if self.local_domain and not self.check_domain_exists(domain) and not self.check_local_domain(domain):
            return { "status": 500, "message": "The domain doesn't exists and doesn't pertain to the %s parent domain" % self.local_domain }

        if not self.check_url_valid_status_code(url):
            return { "status": 500, "message": "The redirection URL doesn't return a valid status code" }

        if self.is_duplicated_in_db(domain):
            return { "status": 500, "message": "The domain already has a redirection" }

        return { "status": 200, "message": "ok " }

    def check_redirection_status(self, redirection):
        domain = redirection.get("domain")
        url = redirection.get("url")

        if not self.check_valid_domain(domain):
            return { "status": 500, "message": "Invalid domain" }

        if not self.check_destination_url(url):
            return { "status": 500, "message": "Invalid redirection url" }

        if self.local_domain and not self.check_domain_exists(domain) and not self.check_local_domain(domain):
            return { "status": 500, "message": "The domain doesn't exists and doesn't pertain to the %s parent domain" % self.local_domain }

        if not self.check_url_valid_status_code(url):
            return { "status": 500, "message": "The redirection URL doesn't return a valid status code" }

        return { "status": 200, "message": "ok " }
