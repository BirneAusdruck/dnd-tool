"""
Settings & Network view.

Shows:
  • Local server URL + QR code  (scan with smartphone to connect)
  • LAN Discovery toggle        (UDP broadcast beacon)
  • Connected clients list
  • Server info (port, version)
"""
from __future__ import annotations
from io import BytesIO

import qrcode
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy, QApplication,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QFont

import requests

from config import Config
from src.gui.theme import COLORS
from src.network.lan_discovery import LanDiscovery, get_local_ip

_VERSION = "0.1.0"
_BASE_URL = f"http://127.0.0.1:{Config.SERVER_PORT}"


def _make_qr_pixmap(url: str, size: int = 180) -> QPixmap | None:
    try:
        qr = qrcode.QRCode(box_size=4, border=3,
                            error_correction=qrcode.constants.ERROR_CORRECT_M)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#1e1e2e", back_color="white")
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        px = QPixmap()
        px.loadFromData(buf.read())
        return px.scaled(size, size,
                         Qt.AspectRatioMode.KeepAspectRatio,
                         Qt.TransformationMode.SmoothTransformation)
    except Exception:
        return None


class SettingsView(QWidget):
    def __init__(self, lan_discovery: LanDiscovery, parent=None):
        super().__init__(parent)
        self._lan = lan_discovery
        self._auth_token: str | None = None
        self._build_ui()
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh_players)
        self._refresh_timer.start(5000)

    def set_auth(self, token: str | None) -> None:
        self._auth_token = token
        self._refresh_players()

    # ── UI construction ───────────────────────────────────────────────────

    def _build_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            f"QScrollArea{{border:none;background:{COLORS['bg']};}}"
        )

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet(f"background:{COLORS['bg']};")
        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(24)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ── Title ──────────────────────────────────────────────────────────
        title = QLabel("Netzwerk & Einstellungen")
        title.setObjectName("title")
        layout.addWidget(title)

        # ── Connection card ────────────────────────────────────────────────
        layout.addWidget(self._section_header("Verbindung"))
        layout.addWidget(self._connection_card())

        # ── LAN Discovery ──────────────────────────────────────────────────
        layout.addWidget(self._section_header("LAN-Discovery"))
        layout.addWidget(self._discovery_card())

        # ── Connected clients ──────────────────────────────────────────────
        layout.addWidget(self._section_header("Verbundene Spieler"))
        self._players_card = self._players_widget()
        layout.addWidget(self._players_card)

        # ── Server info ────────────────────────────────────────────────────
        layout.addWidget(self._section_header("Server-Info"))
        layout.addWidget(self._server_info_card())

        layout.addStretch()

    # ── Cards ─────────────────────────────────────────────────────────────

    def _connection_card(self) -> QWidget:
        card = self._card()
        hlayout = QHBoxLayout(card)
        hlayout.setSpacing(24)

        # Left: URL info
        info = QVBoxLayout()
        info.setSpacing(8)

        local_ip  = get_local_ip()
        local_url = f"http://{local_ip}:{Config.SERVER_PORT}"

        lbl_url = QLabel(local_url)
        lbl_url.setStyleSheet(
            f"color:{COLORS['gold']};font-size:16px;font-weight:bold;"
            f"background:{COLORS['surface']};border-radius:4px;padding:8px 12px;"
        )
        lbl_url.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        btn_copy = QPushButton("Kopieren")
        btn_copy.setObjectName("secondary-btn")
        btn_copy.setFixedWidth(100)
        btn_copy.clicked.connect(lambda: QApplication.clipboard().setText(local_url))

        hint = QLabel(
            "Spieler öffnen diese URL im Browser oder der App.\n"
            "Für Internet-Spiel: Router-Portweiterleitung auf Port "
            f"{Config.SERVER_PORT} einrichten."
        )
        hint.setStyleSheet(f"color:{COLORS['muted']};font-size:11px;")
        hint.setWordWrap(True)

        info.addWidget(QLabel("Lokale Server-Adresse:"))
        info.addWidget(lbl_url)
        info.addWidget(btn_copy)
        info.addWidget(hint)
        info.addStretch()

        # Right: QR code
        qr_layout = QVBoxLayout()
        qr_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_lbl = QLabel()
        px = _make_qr_pixmap(local_url, 180)
        if px:
            qr_lbl.setPixmap(px)
        else:
            qr_lbl.setText("QR-Code\nnicht verfügbar")
        qr_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_caption = QLabel("Mit Kamera scannen →\nAutomatische Verbindung")
        qr_caption.setStyleSheet(f"color:{COLORS['muted']};font-size:10px;")
        qr_caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_layout.addWidget(qr_lbl)
        qr_layout.addWidget(qr_caption)

        hlayout.addLayout(info, 1)
        hlayout.addLayout(qr_layout)
        return card

    def _discovery_card(self) -> QWidget:
        card = self._card()
        layout = QVBoxLayout(card)
        layout.setSpacing(10)

        desc = QLabel(
            "LAN-Discovery sendet alle 2 Sekunden einen UDP-Broadcast (Port 54321).\n"
            "Die DnD-Tool-App auf Smartphones findet den Server so automatisch."
        )
        desc.setStyleSheet(f"color:{COLORS['muted']};font-size:12px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        row = QHBoxLayout()
        self._disc_status = QLabel()
        self._disc_btn = QPushButton()
        self._disc_btn.setFixedWidth(140)
        self._disc_btn.clicked.connect(self._toggle_discovery)
        self._update_discovery_ui()

        row.addWidget(self._disc_status)
        row.addStretch()
        row.addWidget(self._disc_btn)
        layout.addLayout(row)
        return card

    def _players_widget(self) -> QWidget:
        card = self._card()
        layout = QVBoxLayout(card)
        layout.setSpacing(6)

        self._players_layout = QVBoxLayout()
        self._players_layout.setSpacing(4)
        layout.addLayout(self._players_layout)

        btn_refresh = QPushButton("Aktualisieren")
        btn_refresh.setObjectName("secondary-btn")
        btn_refresh.setFixedWidth(130)
        btn_refresh.clicked.connect(self._refresh_players)
        layout.addWidget(btn_refresh)
        return card

    def _server_info_card(self) -> QWidget:
        card = self._card()
        layout = QVBoxLayout(card)
        layout.setSpacing(6)

        rows = [
            ("Version",       _VERSION),
            ("Port",          str(Config.SERVER_PORT)),
            ("API-Basis-URL", f"http://…:{Config.SERVER_PORT}/api"),
            ("WebSocket",     f"ws://…:{Config.SERVER_PORT}  (socket.io)"),
            ("Auth-Methode",  "JWT Bearer Token"),
        ]
        for key, val in rows:
            row = QHBoxLayout()
            k = QLabel(key + ":")
            k.setFixedWidth(130)
            k.setStyleSheet(f"color:{COLORS['muted']};font-size:12px;")
            v = QLabel(val)
            v.setStyleSheet(f"color:{COLORS['text']};font-size:12px;")
            v.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            row.addWidget(k)
            row.addWidget(v)
            row.addStretch()
            layout.addLayout(row)
        return card

    # ── Helpers ───────────────────────────────────────────────────────────

    def _card(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(
            f"background:{COLORS['surface']};border-radius:8px;"
        )
        return w

    def _section_header(self, title: str) -> QLabel:
        lbl = QLabel(title)
        lbl.setStyleSheet(
            f"color:{COLORS['muted']};font-size:11px;font-weight:bold;"
            f"text-transform:uppercase;letter-spacing:1px;"
        )
        return lbl

    # ── Actions ───────────────────────────────────────────────────────────

    def _toggle_discovery(self) -> None:
        if self._lan.is_running():
            self._lan.stop()
        else:
            self._lan.start()
        self._update_discovery_ui()

    def _update_discovery_ui(self) -> None:
        if self._lan.is_running():
            self._disc_status.setText("● Aktiv")
            self._disc_status.setStyleSheet(f"color:{COLORS['success']};font-size:13px;font-weight:bold;")
            self._disc_btn.setText("Discovery stoppen")
            self._disc_btn.setObjectName("secondary-btn")
        else:
            self._disc_status.setText("○ Inaktiv")
            self._disc_status.setStyleSheet(f"color:{COLORS['muted']};font-size:13px;")
            self._disc_btn.setText("Discovery starten")
            self._disc_btn.setObjectName("primary-btn")
        # Force style refresh
        self._disc_btn.style().unpolish(self._disc_btn)
        self._disc_btn.style().polish(self._disc_btn)

    def _refresh_players(self) -> None:
        # Clear old widgets
        while self._players_layout.count():
            item = self._players_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self._auth_token:
            lbl = QLabel("Nicht angemeldet.")
            lbl.setStyleSheet(f"color:{COLORS['muted']};font-size:12px;")
            self._players_layout.addWidget(lbl)
            return

        try:
            r = requests.get(
                f"{_BASE_URL}/api/session/stats",
                headers={"Authorization": f"Bearer {self._auth_token}"},
                timeout=2,
            )
            if r.ok:
                data = r.json()
                players = data.get("players", [])
                if not players:
                    lbl = QLabel("Keine Spieler verbunden.")
                    lbl.setStyleSheet(f"color:{COLORS['muted']};font-size:12px;")
                    self._players_layout.addWidget(lbl)
                else:
                    for p in players:
                        row = QHBoxLayout()
                        icon = "👑" if p.get("role") == "gm" else "🧙"
                        name = QLabel(f"{icon}  {p.get('username', '?')}")
                        name.setStyleSheet(f"color:{COLORS['text']};font-size:12px;")
                        role_lbl = QLabel(p.get("role", "").upper())
                        role_lbl.setStyleSheet(f"color:{COLORS['muted']};font-size:11px;")
                        row.addWidget(name)
                        row.addStretch()
                        row.addWidget(role_lbl)
                        w = QWidget()
                        w.setLayout(row)
                        self._players_layout.addWidget(w)
        except Exception:
            lbl = QLabel("Server nicht erreichbar.")
            lbl.setStyleSheet(f"color:{COLORS['error']};font-size:12px;")
            self._players_layout.addWidget(lbl)
