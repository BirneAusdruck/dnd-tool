"""
SocketIO event handlers for chat messages.
"""
from __future__ import annotations
from collections import deque
from datetime import datetime

from flask import request

from src.server.extensions import socketio
from src.server.rooms.events import _connected

_history: deque[dict] = deque(maxlen=200)


def get_chat_history() -> list[dict]:
    return list(_history)


def _sender_info() -> dict:
    return _connected.get(request.sid, {"username": "Unbekannt", "role": "player"})


def _now() -> str:
    return datetime.now().strftime("%H:%M")


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
