import urllib2

import flask
api_app = flask.Blueprint("api_app", __name__, template_folder="../templates")

@api_app.route("/api", methods=["GET"])
def index():
    lsm = flask_lsm_auth.LSM()

    return flask.render_template("deploy.html", user=lsm.get_login())
