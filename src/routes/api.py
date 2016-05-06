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
validations = Validations(db, config.get("domain"))
dns = DNS(config.get("domain"))

@api_app.route("/api/red/local_domain", methods=["GET"])
def local_domain():
    return flask.jsonify({ "domain": config.get('domain').get('name', '') })

@api_app.route("/api/red", methods=["GET"])
def index():
    return flask.jsonify({ "rows": db.get_redirections() })

@api_app.route("/api/red", methods=["POST"])
def add():
    domain = flask.request.json["domain"].lower().strip()
    url = flask.request.json["url"].lower().strip()
    alternative = flask.request.json["alt"]

    result = validations.check_redirection_can_be_added(domain, url)

    if result.get("status") == 500:
        return flask.make_response(flask.jsonify(result), 500)

    if not dns.add_domain(domain):
        result = { "status": 500, "message": "The domain couldn't be added to the DNS"}
        return flask.make_response(flask.jsonify(result), 500)

    db.add_redirection({ "domain": domain, "url": url})

    if alternative:
        altdomain = 'www.' + domain
        dns.add_domain(altdomain)
        db.add_redirection({ "domain": altdomain, "url": url})

    return flask.make_response(flask.jsonify(result), result.get("status"))

@api_app.route("/api/red", methods=["DELETE"])
def delete():
    id = flask.request.json["id"]
    domain = db.get_redirection(id).get("domain")
    db.del_redirection(id)
    dns.delete_domain(domain)
    return flask.jsonify({ "status": "ok" })

@api_app.route("/api/red/generate", methods=["POST"])
def generate():
    result = nginx.apply_conf()
    return flask.make_response(flask.jsonify(result), result.get("status"))
