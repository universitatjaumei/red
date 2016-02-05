from rfc3987 import parse
import socket
import re

class Validations:
    @staticmethod
    def check_valid_hostname(hostname):
        pattern = re.compile(
            r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
            r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
            r'([a-zA-Z0-9][-_.a-zA-Z0-9]{1,61}[a-zA-Z0-9]))\.'
            r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$'
        )

        return pattern.search(hostname)

    @staticmethod
    def check_destination_url(url):
        try:
            o = parse(url)
            return o.get('scheme') and o.get('authority')
        except ValueError:
            return False

    @staticmethod
    def check_domain_exists(hostname):
        try:
            socket.gethostbyname(hostname)
            return True
        except socket.gaierror:
            return False

    @staticmethod
    def check_uji_domain(hostname):
        pattern = re.compile(
            r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
            r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
            r'([a-zA-Z0-9][-_.a-zA-Z0-9]{1,61}[a-zA-Z0-9]))\.'
            r'uji.es$'
        )
        return pattern.search(hostname)
