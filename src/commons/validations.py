from rfc3987 import parse
import socket
import re
import urllib2

class Validations:
    def __init__(self, db):
        self.db = db

    def check_valid_hostname(self, hostname):
        pattern = re.compile(
            r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
            r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
            r'([a-zA-Z0-9][-_.a-zA-Z0-9]{1,61}[a-zA-Z0-9]))\.'
            r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$'
        )

        return pattern.search(hostname)

    def check_destination_url(self, url):
        try:
            o = parse(url)
            return o.get('scheme') and o.get('authority')
        except ValueError:
            return False

    def check_domain_exists(self, hostname):
        try:
            socket.gethostbyname(hostname)
            return True
        except socket.gaierror:
            return False

    def check_uji_domain(self, hostname):
        pattern = re.compile(
            r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
            r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
            r'([a-zA-Z0-9][-_.a-zA-Z0-9]{1,61}[a-zA-Z0-9]))\.'
            r'uji.es$'
        )
        return pattern.search(hostname)

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

    def check_redirection_can_be_added(self, hostname, url):
        if not self.check_valid_hostname(hostname):
            return { "status": 500, "message": "Invalid hostname"}

        if not self.check_destination_url(url):
            return { "status": 500, "message": "Invalid redirection url"}

        if not self.check_domain_exists(hostname) and not self.check_uji_domain(hostname):
            return { "status": 500, "message": "The hostname doesn't exists and doesn't pertain to the UJI institution"}

        if not self.check_url_valid_status_code(url):
            return { "status": 500, "message": "The redirection URL doesn't return a valid status code"}

        if self.is_duplicated_in_db(hostname):
            return { "status": 500, "message": "The hostname already has a redirection"}

        return { "status": 200, "message": "ok "}
