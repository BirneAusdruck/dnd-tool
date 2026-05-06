"""
Qt-friendly SocketIO client wrapper.

Runs the python-socketio client in a daemon thread and emits PySide6
signals when server events arrive (thread-safe via Qt's queued connections).
"""
from __future__ import annotations
import threading

import socketio as _sio_lib
from PySide6.QtCore import QObject, Signal


class SIOClient(QObject):
    """Thin QObject wrapper around socketio.Client."""

    connected_sig    = Signal()
    disconnected_sig = Signal()

    # Chat / dice
    chat_message_received  = Signal(dict)   # {type, sender, role, text, timestamp}
    dice_result_received   = Signal(dict)   # {type, sender, expr, result, formatted, ...}
    dice_error_received    = Signal(str)    # error string

    # VTT real-time
    token_moved_received   = Signal(str, float, float)  # id, x, y
    fog_updated_received   = Signal(list)               # changes
    vtt_state_received     = Signal(dict)               # full state

    # Presence
    player_joined_received = Signal(dict)
    player_left_received   = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._sio = _sio_lib.Client(reconnection=True, reconnection_attempts=5, logger=False)
        self._username: str = ""
        self._thread: threading.Thread | None = None
        self._register_handlers()

    # ── Connection ────────────────────────────────────────────────────────

    def connect_to_server(self, url: str, token: str, username: str = "") -> None:
        self._username = username
        self._disconnect_thread()

        def _run():
            try:
                self._sio.connect(url, auth={"token": token}, transports=["websocket", "polling"])
                self._sio.wait()
            except Exception:
                pass

        self._thread = threading.Thread(target=_run, daemon=True, name="sio-client")
        self._thread.start()

    def disconnect_from_server(self) -> None:
        try:
            self._sio.disconnect()
        except Exception:
            pass

    def is_connected(self) -> bool:
        return self._sio.connected

    # ── Emit helpers ──────────────────────────────────────────────────────

    def send_chat(self, text: str) -> None:
        self._emit("chat_message", {"text": text})

    def send_dice_roll(self, expr: str, is_private: bool = False) -> None:
        self._emit("dice_roll", {"expr": expr, "is_private": is_private})

    def send_token_move(self, token_id: str, x: float, y: float) -> None:
        self._emit("token_move", {"token_id": token_id, "x": x, "y": y})

    def request_sync(self) -> None:
        self._emit("sync_request", {})

    # ── Internal ──────────────────────────────────────────────────────────

    def _emit(self, event: str, data: dict) -> None:
        if self._sio.connected:
            try:
                self._sio.emit(event, data)
            except Exception:
                pass

    def _disconnect_thread(self) -> None:
        if self._sio.connected:
            try:
                self._sio.disconnect()
            except Exception:
                pass

    def _register_handlers(self) -> None:
        sio = self._sio

        @sio.event
        def connect():
            self.connected_sig.emit()

        @sio.event
        def disconnect():
            self.disconnected_sig.emit()

        @sio.on("chat_message_broadcast")
        def on_chat(data):
            self.chat_message_received.emit(data)

        @sio.on("dice_result_broadcast")
        def on_dice(data):
            self.dice_result_received.emit(data)

        @sio.on("dice_error")
        def on_dice_error(data):
            self.dice_error_received.emit(data.get("error", ""))

        @sio.on("token_moved")
        def on_token_moved(data):
            self.token_moved_received.emit(
                data["token_id"], float(data["x"]), float(data["y"])
            )

        @sio.on("fog_updated")
        def on_fog_updated(data):
            self.fog_updated_received.emit(data.get("changes", []))

        @sio.on("vtt_state_full")
        def on_vtt_state(data):
            self.vtt_state_received.emit(data)

        @sio.on("player_joined")
        def on_player_joined(data):
            self.player_joined_received.emit(data)

        @sio.on("player_left")
        def on_player_left(data):
            self.player_left_received.emit(data)
