import yaml
import os
from docker import Client

class NGINX:
    def __init__(self, db, config):
        self.redConfFile = os.path.join(os.path.dirname(__file__), '..', '..', config.get("red_nginx_conf_file"))
        self.client = Client(base_url="unix://%s" % config.get("socket"))
        self.db = db

    def get_redirect_nginx_conf(self, red):
        return """
server {
	listen 80;
	server_name %(domain)s;
	return 301 %(url)s;
}
""" % red

    def generate_conf(self):
        fd = open(self.redConfFile, "w+")
        for red in self.db.get_redirections():
            fd.write(self.get_redirect_nginx_conf(red))

    def get_nginx_container(self):
        for container in self.client.containers():
            if container.get('Image') == 'nginx':
                return container

    def reload_nginx(self):
        container = self.get_nginx_container()
        self.client.kill(container.get('Id'), 'HUP')

    def apply_conf(self):
        result = { "status": 200, "message": "Nginx configuration applied and service restarted." }
        self.generate_conf()
        self.reload_nginx()
        return result
