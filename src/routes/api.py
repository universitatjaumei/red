import flask
from commons.database import Database
from commons.nginx import NGINX
from commons.config import Config
from commons.validations import Validations
from commons.dns import DNS

config = Config()
api_app = flask.Blueprint("api_app", __name__, template_folder="../templates")
db = Database(config.get("database"))
nginx = NGINX(db, config.get("nginx"))
validations = Validations(db)
dns = DNS(config.get("dns"))

@api_app.route("/api/red", methods=["GET"])
def index():
    return flask.jsonify({ "rows": db.get_redirections() })

@api_app.route("/api/red", methods=["POST"])
def add():
    hostname = flask.request.json["hostname"].lower().strip()
    url = flask.request.json["url"].lower().strip()

    result = validations.check_redirection_can_be_added(hostname, url)

    if result.get("status") == 500:
        return flask.make_response(flask.jsonify(result), 500)

    if not validations.check_domain_exists(hostname) and not dns.add_domain(hostname):
        result = { "status": 500, "message": "The hostname couldn't be added to the DNS"}
        return flask.make_response(flask.jsonify(result), 500)

    db.add_redirection({ "hostname": hostname, "url": url})
    return flask.make_response(flask.jsonify(result), result.get("status"))

@api_app.route("/api/red", methods=["DELETE"])
def delete():
    id = flask.request.json["id"]
    db.del_redirection(id)
    return flask.jsonify({ "status": "ok" })

@api_app.route("/api/red/generate", methods=["POST"])
def generate():
    result = nginx.apply_conf()
    nginx.check_status()
    return flask.make_response(flask.jsonify(result), result.get("status"))
