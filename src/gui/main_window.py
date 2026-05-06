from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QSizePolicy, QFrame, QSpacerItem,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

import requests

from config import Config
from src.gui.server_thread import FlaskServerThread
from src.gui.theme import COLORS

_BASE_URL = f"http://127.0.0.1:{Config.SERVER_PORT}"

_NAV_ITEMS = [
    ("Dashboard",      0),
    ("Charaktere",     1),
    ("Kampagnen",      2),
    ("VTT",            3),
    ("Chat & Würfeln", 4),
    ("Einstellungen",  5),
]


class _NavButton(QPushButton):
    def __init__(self, label: str, parent=None):
        super().__init__(label, parent)
        self.setObjectName("nav-btn")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(44)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)


class _PlaceholderView(QWidget):
    def __init__(self, title: str, phase: str, features: list[str], parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        lbl_title = QLabel(title)
        lbl_title.setObjectName("title")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_phase = QLabel(f"Kommt in {phase}")
        lbl_phase.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_phase.setStyleSheet(f"color: {COLORS['muted']}; font-size: 13px;")

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_phase)

        for feat in features:
            lbl = QLabel(f"  •  {feat}")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f"color: {COLORS['subtext']}; font-size: 13px;")
            layout.addWidget(lbl)


class MainWindow(QMainWindow):
    def __init__(self, server: FlaskServerThread):
        super().__init__()
        self.server = server
        self.auth_token: str | None = None
        self.current_user: dict | None = None

        from src.network.lan_discovery import LanDiscovery
        from config import Config
        self._lan = LanDiscovery(Config.SERVER_PORT)

        self.setWindowTitle("DnD Tool — GM Edition")
        self.setMinimumSize(1200, 780)

        self._build_ui()
        self._check_auth_state()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())

        self.stack = QStackedWidget()
        self._add_views()
        root.addWidget(self.stack, 1)

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(4)

        # App title
        title = QLabel("⚔ DnD Tool")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['accent']}; padding: 8px 4px 16px 4px;")
        layout.addWidget(title)

        # Separator
        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep)
        layout.addSpacing(8)

        # Nav buttons
        self._nav_buttons: list[_NavButton] = []
        self._nav_group = []
        for label, index in _NAV_ITEMS:
            btn = _NavButton(label)
            btn.clicked.connect(lambda checked, i=index, b=btn: self._nav_clicked(i, b))
            self._nav_buttons.append(btn)
            layout.addWidget(btn)

        layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Separator
        sep2 = QFrame()
        sep2.setObjectName("separator")
        sep2.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep2)
        layout.addSpacing(8)

        # User info
        self.lbl_user = QLabel("Nicht angemeldet")
        self.lbl_user.setStyleSheet(f"color: {COLORS['muted']}; font-size: 12px; padding: 4px;")
        self.lbl_user.setWordWrap(True)
        layout.addWidget(self.lbl_user)

        # Logout button (hidden until logged in)
        self.btn_logout = QPushButton("Abmelden")
        self.btn_logout.setObjectName("secondary-btn")
        self.btn_logout.setVisible(False)
        self.btn_logout.clicked.connect(self._logout)
        layout.addWidget(self.btn_logout)

        return sidebar

    def _add_views(self) -> None:
        from src.gui.views.dashboard import DashboardView
        from src.gui.views.characters_view import CharactersView
        from src.gui.views.vtt_view import VTTView
        from src.gui.views.chat_dice_view import ChatDiceView
        from src.gui.client.sio_client import SIOClient

        self.dashboard_view = DashboardView(_BASE_URL)
        self.stack.addWidget(self.dashboard_view)  # index 0

        self.characters_view = CharactersView(_BASE_URL)
        self.characters_view.open_sheet_requested.connect(self._open_character_sheet)
        self.stack.addWidget(self.characters_view)   # index 1

        from src.gui.views.campaigns_view import CampaignsView
        self.campaigns_view = CampaignsView(_BASE_URL)
        self.stack.addWidget(self.campaigns_view)    # index 2

        self.vtt_view = VTTView(_BASE_URL)
        self.stack.addWidget(self.vtt_view)          # index 3

        self.chat_dice_view = ChatDiceView()
        self.stack.addWidget(self.chat_dice_view)    # index 4

        from src.gui.views.settings_view import SettingsView
        self.settings_view = SettingsView(self._lan)
        self.stack.addWidget(self.settings_view)     # index 5

        self._sio_client = SIOClient(self)

        # Activate first nav button
        if self._nav_buttons:
            self._nav_buttons[0].setChecked(True)

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _nav_clicked(self, index: int, clicked_btn: _NavButton) -> None:
        for btn in self._nav_buttons:
            btn.setChecked(False)
        clicked_btn.setChecked(True)
        self.stack.setCurrentIndex(index)

    # ------------------------------------------------------------------
    # Auth flow
    # ------------------------------------------------------------------

    def _check_auth_state(self) -> None:
        from src.gui.dialogs.auth_dialog import AuthDialog
        try:
            r = requests.get(f"{_BASE_URL}/api/auth/has-gm", timeout=3)
            has_gm = r.json().get("has_gm", False)
        except Exception:
            has_gm = False

        mode = "login" if has_gm else "setup"
        dlg = AuthDialog(_BASE_URL, mode=mode, parent=self)
        if dlg.exec() and dlg.token:
            self._on_login_success(dlg.token, dlg.user)
        else:
            # User closed dialog — quit
            from PySide6.QtWidgets import QApplication
            QApplication.quit()

    def _on_login_success(self, token: str, user: dict) -> None:
        self.auth_token = token
        self.current_user = user
        is_gm = user.get("role") == "gm"
        username = user.get("username", "")
        self.dashboard_view.set_auth(token)
        self.characters_view.set_auth(token)
        self.campaigns_view.set_auth(token)
        self.vtt_view.set_auth(token, is_gm=is_gm)
        self._sio_client.connect_to_server(_BASE_URL, token, username)
        self.chat_dice_view.set_client(self._sio_client, username)
        self.settings_view.set_auth(token)
        self._lan.start()
        self.lbl_user.setText(f"{username}\n({user['role'].upper()})")
        self.lbl_user.setStyleSheet(f"color: {COLORS['subtext']}; font-size: 12px; padding: 4px;")
        self.btn_logout.setVisible(True)

    def _open_character_sheet(self, char: dict) -> None:
        from src.gui.views.character_sheet import CharacterSheet
        dlg = CharacterSheet(char, _BASE_URL, self.auth_token, parent=self)
        dlg.exec()
        self.characters_view.refresh()

    def _logout(self) -> None:
        self.auth_token = None
        self.current_user = None
        self.dashboard_view.set_auth(None)
        self.characters_view.set_auth(None)
        self.campaigns_view.set_auth(None)
        self.vtt_view.set_auth(None, is_gm=False)
        self._sio_client.disconnect_from_server()
        self.chat_dice_view.clear_client()
        self.settings_view.set_auth(None)
        self._lan.stop()
        self.lbl_user.setText("Nicht angemeldet")
        self.lbl_user.setStyleSheet(f"color: {COLORS['muted']}; font-size: 12px; padding: 4px;")
        self.btn_logout.setVisible(False)
        self._check_auth_state()
