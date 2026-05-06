"""
Chat & Dice view — combines DicePanel (left) with ChatPanel (right).
Wired to a SIOClient for real-time sync.
"""
from __future__ import annotations

from PySide6.QtWidgets import QWidget, QHBoxLayout, QSplitter
from PySide6.QtCore import Qt

from src.gui.widgets.chat_panel import ChatPanel
from src.gui.widgets.dice_panel import DicePanel
from src.gui.theme import COLORS


class ChatDiceView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._client = None
        self._username = ""
        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(
            f"QSplitter::handle{{background:{COLORS['border']};width:1px;}}"
        )

        # Left: dice panel (fixed-ish width)
        self.dice_panel = DicePanel()
        self.dice_panel.setMinimumWidth(220)
        self.dice_panel.setMaximumWidth(340)
        self.dice_panel.setStyleSheet(f"background:{COLORS['sidebar']};")
        self.dice_panel.roll_requested.connect(self._on_roll_requested)
        splitter.addWidget(self.dice_panel)

        # Right: chat panel
        self.chat_panel = ChatPanel()
        self.chat_panel.message_send.connect(self._on_message_send)
        splitter.addWidget(self.chat_panel)

        splitter.setSizes([260, 600])
        layout.addWidget(splitter)

    # ── Client wiring ─────────────────────────────────────────────────────

    def set_client(self, client, username: str = "") -> None:
        """Connect to a SIOClient instance after login."""
        if self._client is not None:
            self._disconnect_client()

        self._client = client
        self._username = username

        client.chat_message_received.connect(self.chat_panel.add_message)
        client.dice_result_received.connect(self._on_dice_result)
        client.dice_error_received.connect(self._on_dice_error)
        client.connected_sig.connect(self._on_connected)
        client.disconnected_sig.connect(self._on_disconnected)
        client.player_joined_received.connect(self._on_player_joined)
        client.player_left_received.connect(self._on_player_left)

    def clear_client(self) -> None:
        self._disconnect_client()
        self._client = None
        self._username = ""

    # ── Event handlers ────────────────────────────────────────────────────

    def _on_roll_requested(self, expr: str, is_private: bool) -> None:
        if self._client and self._client.is_connected():
            self._client.send_dice_roll(expr, is_private)
        else:
            # Offline fallback: roll locally and show only in dice panel
            from src.game.dice import roll as dice_roll
            try:
                result = dice_roll(expr)
                self.dice_panel.show_last_result(result.format())
                self.chat_panel.add_system(
                    f"[Offline] {expr} → {result.format()}"
                )
            except ValueError as e:
                self.chat_panel.add_system(f"Fehler: {e}")

    def _on_message_send(self, text: str) -> None:
        if self._client and self._client.is_connected():
            self._client.send_chat(text)
        else:
            self.chat_panel.add_system("[Offline] Nicht verbunden.")

    def _on_dice_result(self, data: dict) -> None:
        self.chat_panel.add_dice_result(data)
        if data.get("sender") == self._username:
            self.dice_panel.show_last_result(data.get("formatted", ""))

    def _on_dice_error(self, error: str) -> None:
        self.chat_panel.add_system(f"Würfelfehler: {error}")

    def _on_connected(self) -> None:
        self.chat_panel.add_system("● Verbunden mit dem Server.")

    def _on_disconnected(self) -> None:
        self.chat_panel.add_system("○ Verbindung getrennt.")

    def _on_player_joined(self, data: dict) -> None:
        name = data.get("username", "?")
        self.chat_panel.add_system(f"→ {name} hat die Sitzung betreten.")

    def _on_player_left(self, data: dict) -> None:
        name = data.get("username", "?")
        self.chat_panel.add_system(f"← {name} hat die Sitzung verlassen.")

    def _disconnect_client(self) -> None:
        if self._client is None:
            return
        try:
            self._client.chat_message_received.disconnect(self.chat_panel.add_message)
            self._client.dice_result_received.disconnect(self._on_dice_result)
            self._client.dice_error_received.disconnect(self._on_dice_error)
            self._client.connected_sig.disconnect(self._on_connected)
            self._client.disconnected_sig.disconnect(self._on_disconnected)
            self._client.player_joined_received.disconnect(self._on_player_joined)
            self._client.player_left_received.disconnect(self._on_player_left)
        except RuntimeError:
            pass
