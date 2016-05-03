import flask
import flask_lsm_auth
from routes.api import api_app
import yaml
import os
from commons.config import Config

config = Config()
auth_config = config.get("auth")
authorizedUsers = auth_config.get("users")

app = flask.Flask("redirect")
app.register_blueprint(api_app)

@app.route("/", methods=["GET"])
def index():
    lsm = flask_lsm_auth.LSM(auth_config)
    return flask.render_template("redirection.html", section="redirection", user=lsm.get_login())

@app.route("/logout", methods=["GET"])
def logout():
    lsm = flask_lsm_auth.LSM(auth_config)
    lsm.logout(flask.request.url_root)
    return lsm.compose_response()

@app.after_request
def after_request(res):
    lsm = flask_lsm_auth.LSM(auth_config)
    user = lsm.get_login()
    if not user:
        lsm.login()
    elif not user in authorizedUsers:
        return flask.Response("You're not authorized to access this application.", 401)

    return lsm.compose_response(res)

if __name__ == "__main__":
    port = config.get("port")
    app.run(host="0.0.0.0", debug=False)
