"""
VTT state REST endpoints.

GET  /api/vtt/state  — returns current VTT state
PUT  /api/vtt/state  — GM updates full state, broadcasts via SocketIO
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt

from src.server.vtt.events import get_vtt_state, set_vtt_state
from src.server.extensions import socketio

vtt_bp = Blueprint("vtt", __name__)


@vtt_bp.route("/state", methods=["GET"])
@jwt_required()
def get_state():
    return jsonify(get_vtt_state()), 200


@vtt_bp.route("/state", methods=["PUT"])
@jwt_required()
def put_state():
    claims = get_jwt()
    role = claims.get("role", "player")
    if role != "gm":
        return jsonify({"error": "Nur der GM darf den VTT-Status setzen."}), 403

    data = request.get_json(force=True) or {}
    set_vtt_state(data)
    socketio.emit("vtt_state_full", get_vtt_state())
    return jsonify({"ok": True}), 200
