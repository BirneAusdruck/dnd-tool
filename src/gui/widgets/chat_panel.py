"""
Chat panel widget — displays messages and dice results, has a text input.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser,
    QLineEdit, QPushButton, QLabel, QFrame,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from src.gui.theme import COLORS


class ChatPanel(QWidget):
    """Scrolling chat + dice result log with a text input bar."""

    message_send = Signal(str)   # emitted when user presses Enter / Send

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QLabel("💬 Chat & Würfelergebnisse")
        header.setStyleSheet(
            f"color:{COLORS['accent']};font-weight:bold;font-size:13px;"
            f"padding:6px 8px;background:{COLORS['sidebar']};"
            f"border-bottom:1px solid {COLORS['border']};"
        )
        layout.addWidget(header)

        self._log = QTextBrowser()
        self._log.setOpenExternalLinks(False)
        self._log.setStyleSheet(
            f"QTextBrowser{{background:{COLORS['bg']};color:{COLORS['text']};"
            f"border:none;font-size:12px;padding:4px;}}"
        )
        layout.addWidget(self._log, 1)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color:{COLORS['border']};")
        layout.addWidget(sep)

        # Input bar
        input_row = QHBoxLayout()
        input_row.setContentsMargins(6, 4, 6, 4)
        input_row.setSpacing(4)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Nachricht schreiben …")
        self._input.setStyleSheet(
            f"background:{COLORS['surface']};color:{COLORS['text']};"
            f"border:1px solid {COLORS['border']};border-radius:4px;"
            f"padding:4px 6px;font-size:12px;"
        )
        self._input.returnPressed.connect(self._on_send)

        btn_send = QPushButton("→")
        btn_send.setObjectName("primary-btn")
        btn_send.setFixedWidth(36)
        btn_send.setFixedHeight(28)
        btn_send.clicked.connect(self._on_send)

        input_row.addWidget(self._input, 1)
        input_row.addWidget(btn_send)
        layout.addLayout(input_row)

    # ── Public API ────────────────────────────────────────────────────────

    def add_message(self, data: dict) -> None:
        """Append a chat message."""
        sender = data.get("sender", "?")
        text   = data.get("text", "")
        ts     = data.get("timestamp", "")
        role   = data.get("role", "player")

        name_color = COLORS["accent"] if role == "gm" else COLORS["gold"]
        html = (
            f'<span style="color:{COLORS["muted"]};font-size:10px;">[{ts}]</span> '
            f'<b style="color:{name_color};">{_esc(sender)}</b>: '
            f'<span style="color:{COLORS["text"]};">{_esc(text)}</span>'
        )
        self._append(html)

    def add_dice_result(self, data: dict) -> None:
        """Append a dice roll result."""
        sender    = data.get("sender", "?")
        expr      = data.get("expr", "?")
        formatted = data.get("formatted", "?")
        ts        = data.get("timestamp", "")
        is_priv   = data.get("is_private", False)
        result    = data.get("result", {})

        is_crit   = result.get("is_critical", False)
        is_fumble = result.get("is_fumble", False)

        if is_crit:
            suffix = ' <b style="color:#f5c518;"> ★ KRITISCH!</b>'
        elif is_fumble:
            suffix = ' <b style="color:#f38ba8;"> ✗ PATZER!</b>'
        else:
            suffix = ""

        priv_tag = ' <i style="color:#888;">(geheim)</i>' if is_priv else ""
        total    = result.get("total", "?")

        html = (
            f'<span style="color:{COLORS["muted"]};font-size:10px;">[{ts}]</span> '
            f'<b style="color:{COLORS["accent"]};">🎲 {_esc(sender)}</b> '
            f'wirft <code style="color:{COLORS["gold"]};">{_esc(expr)}</code>{priv_tag}: '
            f'<span style="color:{COLORS["text"]};">{_esc(formatted)}</span>'
            f'{suffix}'
        )
        self._append(html)

    def add_system(self, text: str) -> None:
        html = f'<i style="color:{COLORS["muted"]};font-size:11px;">{_esc(text)}</i>'
        self._append(html)

    def clear_log(self) -> None:
        self._log.clear()

    # ── Private ───────────────────────────────────────────────────────────

    def _append(self, html: str) -> None:
        self._log.append(html)
        sb = self._log.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _on_send(self) -> None:
        text = self._input.text().strip()
        if text:
            self.message_send.emit(text)
            self._input.clear()


def _esc(text: str) -> str:
    """Minimal HTML escaping."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))
