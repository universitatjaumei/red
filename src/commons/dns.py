import yaml
import os

class DNS:
    def __init__(self, config):
        self.api_url = os.path.join(os.path.dirname(__file__), '..', '..', config.get("api_url"))

    # TODO: add the domain name to the local DNS
    def add_domain(self, domain):
        return True
