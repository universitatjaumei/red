import flask
from commons.sqlite import Database
from commons.nginx import NGINX
from commons.config import Config
from commons.validations import Validations
from commons.dns import DNS
from commons.oracle import OracleDatabase

config = Config()
api_app = flask.Blueprint("api_app", __name__, template_folder="../templates")
db = Database(config.get("database"))
nginx = NGINX(db, config.get("nginx"))
validations = Validations(db, config.get("domain"))
oracle_conn = config.get("domain").get("db_conn")
dns = DNS(config.get("domain"), OracleDatabase(oracle_conn))

@api_app.route("/api/red/local_domain", methods=["GET"])
def local_domain():
    return flask.jsonify({ "domain": config.get('domain').get('name', '') })

@api_app.route("/api/red", methods=["GET"])
def index():
    return flask.jsonify({ "rows": db.get_redirections() })

@api_app.route("/api/red", methods=["POST"])
def add():
    domain = flask.request.json["domain"].lower().strip()
    url = flask.request.json["url"].strip()
    alternative = flask.request.json["alt"]

    result = validations.check_redirection_can_be_added(domain, url)

    if result.get("status") == 500:
        return flask.make_response(flask.jsonify(result), 500)

    if not dns.add_domain(domain):
        result = { "status": 500, "message": "The domain couldn't be added to the DNS, but the redirection has been added"}

    db.add_redirection({ "domain": domain, "url": url})

    if alternative:
        altdomain = 'www.' + domain
        dns.add_domain(altdomain)
        db.add_redirection({ "domain": altdomain, "url": url})

    return flask.make_response(flask.jsonify(result), result.get("status"))

@api_app.route("/api/red/<id>", methods=["DELETE"])
def delete(id):
    domain = db.get_redirection(id).get("domain")
    db.del_redirection(id)
    dns.delete_domain(domain)
    return flask.jsonify({ "status": 200 })

@api_app.route("/api/red/<id>", methods=["PUT"])
def put(id):
    redirect = flask.request.json["redirect"]
    if not validations.check_destination_url(redirect):
        return flask.jsonify({ "status": 500, "message": "Invalid redirection URL" })

    db.update_redirection(id, redirect)
    return flask.jsonify({ "status": 200 })

@api_app.route("/api/red/generate", methods=["POST"])
def generate():
    result = nginx.apply_conf()

    if (result.get("status") != 200):
        return flask.make_response(flask.jsonify(result), result.get("status"))

    result = dns.generate_zone()
    return flask.make_response(flask.jsonify(result), result.get("status"))
