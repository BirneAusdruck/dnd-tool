from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGroupBox, QGridLayout, QSizePolicy, QScrollArea, QFrame,
)
from PySide6.QtCore import Qt, QTimer

import requests

from src.utils.network import get_local_ip
from src.client.gui.theme import COLORS
from config import Config


class _StatCard(QGroupBox):
    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(4)

        self.value_lbl = QLabel("—")
        self.value_lbl.setObjectName("stat-value")
        self.value_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl = QLabel(label.upper())
        lbl.setObjectName("stat-label")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.value_lbl)
        layout.addWidget(lbl)
        self.setMinimumHeight(90)

    def set_value(self, text: str) -> None:
        self.value_lbl.setText(text)


class DashboardView(QWidget):
    def __init__(self, base_url: str, parent=None):
        super().__init__(parent)
        self.base_url = base_url
        self._auth_token: str | None = None
        self._local_ip = get_local_ip()
        self._build_ui()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(5000)

    def set_auth(self, token: str | None) -> None:
        self._auth_token = token
        self._refresh()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Page title
        title = QLabel("Dashboard")
        title.setObjectName("title")
        layout.addWidget(title)

        # --- Server info group ---
        server_grp = QGroupBox("Server")
        server_layout = QGridLayout(server_grp)
        server_layout.setSpacing(12)

        self._status_lbl = QLabel("● Online")
        self._status_lbl.setObjectName("status-online")

        self._url_lbl = QLabel(f"http://{self._local_ip}:{Config.SERVER_PORT}")
        self._url_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._url_lbl.setStyleSheet(f"color: {COLORS['gold']}; font-family: monospace; font-size: 14px;")

        self._port_lbl = QLabel(str(Config.SERVER_PORT))

        server_layout.addWidget(QLabel("Status:"),    0, 0, Qt.AlignmentFlag.AlignRight)
        server_layout.addWidget(self._status_lbl,      0, 1)
        server_layout.addWidget(QLabel("URL:"),        1, 0, Qt.AlignmentFlag.AlignRight)
        server_layout.addWidget(self._url_lbl,         1, 1)
        server_layout.addWidget(QLabel("Port:"),       2, 0, Qt.AlignmentFlag.AlignRight)
        server_layout.addWidget(self._port_lbl,        2, 1)
        server_layout.setColumnStretch(1, 1)
        layout.addWidget(server_grp)

        # --- Stats row ---
        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)

        self._card_players = _StatCard("Spieler verbunden")
        self._card_players.set_value("0")
        stats_row.addWidget(self._card_players)

        self._card_campaigns = _StatCard("Kampagnen")
        self._card_campaigns.set_value("—")
        stats_row.addWidget(self._card_campaigns)

        self._card_characters = _StatCard("Charaktere")
        self._card_characters.set_value("—")
        stats_row.addWidget(self._card_characters)

        layout.addLayout(stats_row)

        # --- Connected players list ---
        players_grp = QGroupBox("Verbundene Spieler")
        players_layout = QVBoxLayout(players_grp)
        self._players_container = QVBoxLayout()
        self._players_container.setSpacing(4)
        self._no_players_lbl = QLabel("Noch keine Spieler verbunden.")
        self._no_players_lbl.setStyleSheet(f"color: {COLORS['muted']}; font-style: italic;")
        self._players_container.addWidget(self._no_players_lbl)
        players_layout.addLayout(self._players_container)
        layout.addWidget(players_grp)

        layout.addStretch()

    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------

    def _refresh(self) -> None:
        if not self._auth_token:
            return
        try:
            headers = {"Authorization": f"Bearer {self._auth_token}"}
            r = requests.get(f"{self.base_url}/api/session/stats", headers=headers, timeout=2)
            if r.status_code == 200:
                data = r.json()
                count = data.get("connected_players", 0)
                players = data.get("players", [])
                self._card_players.set_value(str(count))
                self._update_player_list(players)
        except Exception:
            pass

    def _update_player_list(self, players: list[dict]) -> None:
        while self._players_container.count():
            item = self._players_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not players:
            self._no_players_lbl = QLabel("Noch keine Spieler verbunden.")
            self._no_players_lbl.setStyleSheet(f"color: {COLORS['muted']}; font-style: italic;")
            self._players_container.addWidget(self._no_players_lbl)
            return

        for p in players:
            role_color = COLORS["accent"] if p.get("role") == "gm" else COLORS["gold"]
            lbl = QLabel(f"● {p['username']}  [{p.get('role', '?').upper()}]")
            lbl.setStyleSheet(f"color: {role_color}; padding: 2px 0;")
            self._players_container.addWidget(lbl)
