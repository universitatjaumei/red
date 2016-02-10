import yaml
import os

class DNS:
    def __init__(self, config):
        self.api_url = config.get("api_url")

    # TODO: add the domain name to the local DNS
    def add_domain(self, domain):
        return True
