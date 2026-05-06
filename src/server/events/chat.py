"""
SocketIO event handlers for chat messages and dice rolls.
"""
from __future__ import annotations
from collections import deque
from datetime import datetime

from flask import request

from src.server.extensions import socketio
from src.server.events import _connected
from src.game.dice import roll as dice_roll, DiceResult

# Rolling message buffer (last 200 messages)
_history: deque[dict] = deque(maxlen=200)


def get_chat_history() -> list[dict]:
    return list(_history)


def _sender_info() -> dict:
    return _connected.get(request.sid, {"username": "Unbekannt", "role": "player"})


def _now() -> str:
    return datetime.now().strftime("%H:%M")


# ── Event handlers ────────────────────────────────────────────────────────

@socketio.on("chat_message")
def on_chat_message(data: dict):
    """
    Client emits {text}.
    Server broadcasts {sender, role, text, timestamp} to all.
    """
    text = str(data.get("text", "")).strip()
    if not text:
        return

    info = _sender_info()
    msg = {
        "type":      "chat",
        "sender":    info["username"],
        "role":      info["role"],
        "text":      text,
        "timestamp": _now(),
    }
    _history.append(msg)
    socketio.emit("chat_message_broadcast", msg)


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
        # Only the roller and the GM see private rolls
        socketio.emit("dice_result_broadcast", msg, to=request.sid)
        for sid, player in _connected.items():
            if player["role"] == "gm" and sid != request.sid:
                socketio.emit("dice_result_broadcast", msg, to=sid)
    else:
        _history.append(msg)
        socketio.emit("dice_result_broadcast", msg)
