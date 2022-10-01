import os

from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO

from db import db
from models import ToDoModel

from resources.ToDo import blp as ToDoBlueprint
from resources.User import blp as UserBlueprint


def create_app(db_url=None):
    app = Flask(__name__)

    app.config['PROPAGATE_EXCEPTION'] = True
    app.config["API_TITLE"] = "ToDoApp REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/ToDo-swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///ToDo.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "320229326840313632469276906211776589187"

    cors = CORS()
    socket = SocketIO(cors_allowed_origins="*")
    socket.init_app(app, cors_allowed_origins='*')
    cors.init_app(app)
    api = Api(app)
    db.init_app(app)
    jwt = JWTManager(app)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "Il token è scaduto.", "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Verifica firma fallita.", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "La richiesta non contiene un access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    @app.before_request
    def create_table():
        db.create_all()

    api.register_blueprint(ToDoBlueprint)
    api.register_blueprint(UserBlueprint)

    return app
