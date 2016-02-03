import yaml
import os
from docker import Client

class NGINX:
    def __init__(self, db):
        nginx_config = self._get_config()
        self.filename = os.path.join(os.path.dirname(__file__), '..', '..', nginx_config.get("filename"))
        self.socket = nginx_config.get("socket")
        self.db = db

    def _get_config(self):
        f = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "config.yml"))
        data = yaml.safe_load(f)
        f.close()
        return data.get("nginx")

    def get_redirect_nginx_conf(self, red):
        return """
server {
	listen 80;
	server_name %(host)s;
	return 301 %(url)s;
}
""" % red

    def generate_conf(self):
        fd = open(self.filename, "w+")
        for red in self.db.get_redirections():
            fd.write(self.get_redirect_nginx_conf(red))

    def reload_nginx(self):
        client = Client(base_url="unix://%s" % self.socket)
        for container in client.containers():
            if container.get('Image') == 'nginx':
                client.kill(container.get('Id'), 'HUP')

    def apply_conf(self):
        self.generate_conf()
        self.reload_nginx()
