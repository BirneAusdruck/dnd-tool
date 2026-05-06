from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from src.server.events import get_connected_count, get_connected_players

session_bp = Blueprint("session", __name__)


@session_bp.route("/stats", methods=["GET"])
@jwt_required()
def stats():
    return jsonify({
        "connected_players": get_connected_count(),
        "players": get_connected_players(),
    }), 200
