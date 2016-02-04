import yaml
import os
from docker import Client

class NGINX:
    def __init__(self, db, config):
        self.filename = os.path.join(os.path.dirname(__file__), '..', '..', config.get("filename"))
        self.socket = config.get("socket")
        self.db = db

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
