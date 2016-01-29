import flask
import flask_lsm_auth
from routes.api import api_app
import yaml
import os

app = flask.Flask("redirect")

app.register_blueprint(api_app)

@app.route("/", methods=["GET"])
def index():
    lsm = flask_lsm_auth.LSM()
    return flask.render_template("redirection.html", section="redirection", user=lsm.get_login())

@app.after_request
def after_request(res):
    lsm = flask_lsm_auth.LSM()
    if not lsm.get_login():
        lsm.login()

    return lsm.compose_response(res)

def _get_webserver_hostname_port():
    f = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "config.yml"))
    data = yaml.safe_load(f)
    f.close()
    return { "host": data.get("webserver").get("host"), "port": data.get("webserver").get("port") }

if __name__ == "__main__":
    conf = _get_webserver_hostname_port()
    app.run(host="0.0.0.0", port=conf["port"], debug=True)
