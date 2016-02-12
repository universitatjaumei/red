import yaml
import os

class DNS:
    def __init__(self, config):
        self.api_url = config.get("dns_api")

    # TODO: add the domain name to the local DNS
    def add_domain(self, domain):
        return True
