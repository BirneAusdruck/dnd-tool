"""
SocketIO event handlers for real-time VTT synchronization.
"""
from __future__ import annotations

from flask_jwt_extended import decode_token
from flask_jwt_extended.exceptions import JWTDecodeError

from src.server.extensions import socketio

# Shared in-memory VTT state (server is authoritative)
_vtt_state: dict = {
    "map_path": "",
    "grid_size": 50,
    "tokens": [],
    "fog_hidden": [],
    "initiative": {},
}


def get_vtt_state() -> dict:
    return _vtt_state


def set_vtt_state(state: dict) -> None:
    _vtt_state.update(state)


# ── Helpers ───────────────────────────────────────────────────────────────

def _sid_role(auth: dict | None) -> str | None:
    """Return 'gm' or 'player' from the JWT in the connect auth dict, or None."""
    if not auth:
        return None
    token = auth.get("token", "")
    try:
        data = decode_token(token)
        return data.get("role") or data.get("sub", {}).get("role")
    except Exception:
        return None


# ── Event handlers ────────────────────────────────────────────────────────

@socketio.on("token_move")
def on_token_move(data):
    """
    Client emits {token_id, x, y}.
    Server updates state and broadcasts to all others.
    """
    token_id = data.get("token_id")
    x = data.get("x", 0.0)
    y = data.get("y", 0.0)

    for token in _vtt_state["tokens"]:
        if token.get("token_id") == token_id:
            token["x"] = x
            token["y"] = y
            break

    socketio.emit("token_moved", {"token_id": token_id, "x": x, "y": y}, include_self=False)


@socketio.on("fog_update")
def on_fog_update(data):
    """
    Client emits {changes: [[row, col, hidden], ...]}.
    Server applies and broadcasts.
    """
    changes = data.get("changes", [])
    hidden_set = {tuple(cell[:2]) for cell in _vtt_state["fog_hidden"]}

    for row, col, hidden in changes:
        key = (row, col)
        if hidden:
            hidden_set.add(key)
        else:
            hidden_set.discard(key)

    _vtt_state["fog_hidden"] = [[r, c] for r, c in hidden_set]
    socketio.emit("fog_updated", {"changes": changes}, include_self=False)


@socketio.on("sync_request")
def on_sync_request():
    """Client requests full VTT state (e.g. on reconnect)."""
    socketio.emit("vtt_state_full", _vtt_state)


@socketio.on("ping_event")
def on_ping_event(data):
    """Broadcast a ping location to all clients."""
    socketio.emit("ping_received", data, include_self=False)
