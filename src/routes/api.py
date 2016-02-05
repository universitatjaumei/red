import flask
from commons.database import Database
from commons.nginx import NGINX
from commons.config import Config
from commons.validations import Validations

config = Config()
api_app = flask.Blueprint("api_app", __name__, template_folder="../templates")
db = Database(config.get("database"))
nginx = NGINX(db, config.get("nginx"))

@api_app.route("/api/red", methods=["GET"])
def index():
    return flask.jsonify({ "rows": db.get_redirections() })

@api_app.route("/api/red", methods=["POST"])
def add():

    hostname = flask.request.json["hostname"].lower().strip()
    url = flask.request.json["url"].lower().strip()

    if not Validations.check_valid_hostname(hostname):
        result = { "status": 500, "message": "Invalid hostname"}
        return flask.make_response(flask.jsonify(result), 500)

    if not Validations.check_destination_url(url):
        result = { "status": 500, "message": "Invalid redirection url"}
        return flask.make_response(flask.jsonify(result), 500)

    if not Validations.check_domain_exists(hostname) and not Validations.check_uji_domain(hostname):
        result = { "status": 500, "message": "The hostname doesn't exists and doesn't pertain to the UJI institution"}
        return flask.make_response(flask.jsonify(result), 500)

    if not Validations.check_url_valid_status_code(url):
        result = { "status": 500, "message": "The redirection URL doesn't return a valid status code"}
        return flask.make_response(flask.jsonify(result), 500)

    db.add_redirection({ "hostname": hostname, "url": url})
    result = { "status": 200, "message": "ok "}
    return flask.make_response(flask.jsonify(result), result.get("status"))

@api_app.route("/api/red", methods=["DELETE"])
def delete():
    id = flask.request.json["id"]
    db.del_redirection(id)
    return flask.jsonify({ "status": "ok" })

@api_app.route("/api/red/generate", methods=["POST"])
def generate():
    result = nginx.apply_conf()
    return flask.make_response(flask.jsonify(result), result.get("status"))
