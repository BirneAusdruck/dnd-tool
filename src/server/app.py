from flask import Flask, jsonify
from config import Config
from src.server.extensions import db, jwt, socketio


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app)

    # Register models so SQLAlchemy picks them up
    from src.persistence.models import user, character, campaign  # noqa: F401

    with app.app_context():
        db.create_all()

    from src.server.routes.auth import auth_bp
    from src.server.rooms.routes import session_bp
    from src.server.routes.characters import characters_bp
    from src.server.routes.campaigns import campaigns_bp
    from src.server.vtt.routes import vtt_bp
    from src.server.routes.discovery import discovery_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(session_bp, url_prefix="/api/session")
    app.register_blueprint(characters_bp, url_prefix="/api/characters")
    app.register_blueprint(campaigns_bp, url_prefix="/api/campaigns")
    app.register_blueprint(vtt_bp, url_prefix="/api/vtt")
    app.register_blueprint(discovery_bp, url_prefix="/api/discovery")

    # CORS headers for mobile clients
    @app.after_request
    def _add_cors(response):
        response.headers.setdefault("Access-Control-Allow-Origin", "*")
        response.headers.setdefault(
            "Access-Control-Allow-Headers", "Content-Type, Authorization"
        )
        response.headers.setdefault(
            "Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS"
        )
        return response

    @app.route("/api/<path:path>", methods=["OPTIONS"])
    def _handle_options(path):
        return "", 204

    from src.server.rooms import events as _rooms_events  # noqa: F401 — registers SocketIO handlers
    from src.server.vtt import events as _vtt_events      # noqa: F401
    from src.server.chat import events as _chat_events    # noqa: F401
    from src.server.dice import events as _dice_events    # noqa: F401

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "version": "0.1.0"}), 200

    return app
