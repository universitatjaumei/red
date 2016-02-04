import flask
from commons.database import Database
from commons.nginx import NGINX
from commons.config import Config

config = Config()
api_app = flask.Blueprint("api_app", __name__, template_folder="../templates")
db = Database(config.get("database"))
nginx = NGINX(db, config.get("nginx"))

@api_app.route("/api/red", methods=["GET"])
def index():
    return flask.jsonify({ "rows": db.get_redirections() })

@api_app.route("/api/red", methods=["POST"])
def add():
    hostname = flask.request.json["hostname"].lower()
    url = flask.request.json["url"].lower()
    db.add_redirection({ "hostname": hostname, "url": url})
    return flask.jsonify({ "status": "ok" })

@api_app.route("/api/red", methods=["DELETE"])
def delete():
    id = flask.request.json["id"]
    db.del_redirection(id)
    return flask.jsonify({ "status": "ok" })

@api_app.route("/api/red/generate", methods=["POST"])
def generate():
    nginx.apply_conf();
    return flask.jsonify({ "status": "ok" })
