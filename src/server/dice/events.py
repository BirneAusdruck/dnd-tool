"""
SocketIO event handlers for dice rolls.
"""
from __future__ import annotations
from datetime import datetime

from flask import request

from src.server.extensions import socketio
from src.server.rooms.events import _connected
from src.server.chat.events import _history
from src.shared.domain.dice import roll as dice_roll, DiceResult


def _sender_info() -> dict:
    return _connected.get(request.sid, {"username": "Unbekannt", "role": "player"})


def _now() -> str:
    return datetime.now().strftime("%H:%M")


@socketio.on("dice_roll")
def on_dice_roll(data: dict):
    """
    Client emits {expr, is_private}.
    Server rolls, then broadcasts result (or only to sender if private).
    """
    expr       = str(data.get("expr", "1d20")).strip()
    is_private = bool(data.get("is_private", False))

    info = _sender_info()

    try:
        result: DiceResult = dice_roll(expr)
    except ValueError as e:
        socketio.emit(
            "dice_error",
            {"error": str(e)},
            to=request.sid,
        )
        return

    msg = {
        "type":       "dice",
        "sender":     info["username"],
        "role":       info["role"],
        "expr":       expr,
        "result":     result.to_dict(),
        "formatted":  result.format(),
        "is_private": is_private,
        "timestamp":  _now(),
    }

    if is_private:
        socketio.emit("dice_result_broadcast", msg, to=request.sid)
        for sid, player in _connected.items():
            if player["role"] == "gm" and sid != request.sid:
                socketio.emit("dice_result_broadcast", msg, to=sid)
    else:
        _history.append(msg)
        socketio.emit("dice_result_broadcast", msg)
