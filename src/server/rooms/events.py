from flask import request
from flask_jwt_extended import decode_token
from src.server.extensions import socketio, db

_connected: dict[str, dict] = {}


@socketio.on("connect")
def on_connect(auth):
    token = auth.get("token") if isinstance(auth, dict) else None
    if not token:
        return False

    try:
        payload = decode_token(token)
        user_id = int(payload["sub"])
        from src.persistence.models.user import User
        user = db.session.get(User, user_id)
        if not user:
            return False
        _connected[request.sid] = {
            "user_id": user_id,
            "username": user.username,
            "role": user.role,
        }
        socketio.emit("player_joined", {"username": user.username, "role": user.role}, broadcast=True)
        return True
    except Exception:
        return False


@socketio.on("disconnect")
def on_disconnect():
    player = _connected.pop(request.sid, None)
    if player:
        socketio.emit("player_left", {"username": player["username"]}, broadcast=True)


def get_connected_count() -> int:
    return len(_connected)


def get_connected_players() -> list[dict]:
    return list(_connected.values())
