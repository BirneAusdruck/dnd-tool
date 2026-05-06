"""
Discovery endpoint — no auth required.
Mobile clients call this after finding the server via UDP broadcast
to get connection details.
"""
from flask import Blueprint, jsonify

from config import Config
from src.network.lan_discovery import get_local_ip

discovery_bp = Blueprint("discovery", __name__)


@discovery_bp.route("/info")
def server_info():
    local_ip = get_local_ip()
    return jsonify({
        "server_name": "DnD Tool GM",
        "version":     "0.1.0",
        "port":        Config.SERVER_PORT,
        "local_ip":    local_ip,
        "url":         f"http://{local_ip}:{Config.SERVER_PORT}",
        "api_base":    f"http://{local_ip}:{Config.SERVER_PORT}/api",
        "socket_url":  f"http://{local_ip}:{Config.SERVER_PORT}",
    }), 200
