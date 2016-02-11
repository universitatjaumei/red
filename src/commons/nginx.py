import yaml
import os
from docker import Client
from datetime import datetime
class NGINX:
    def __init__(self, db, config):
        self.redConfFile = os.path.join(os.path.dirname(__file__), '..', '..', config.get("red_nginx_conf_file"))
        self.client = Client(base_url="unix://%s" % config.get("socket"))
        self.timestamp = datetime.now()
        self.db = db
        for container in self.client.containers():
            if container.get('Image') == 'nginx':
                self.container = container

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

    def reload_nginx(self, container):
        return self.client.kill(self.container.get('Id'), 'HUP')

    def get_result(self):
        result = { "status": 200, "message": "Nginx configuration applied and service restarted." }
        log = self.client.logs(self.container.get('Id'), since=self.timestamp)

        if log:
            result['message'] = log

        return result


    def apply_conf(self):
        self.generate_conf()
        nginx_result = self.reload_nginx(self.container)

        return self.get_result()
