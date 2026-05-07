from PySide6.QtWidgets import (
    QDialog, QTabWidget, QWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QMessageBox, QHBoxLayout,
)
from PySide6.QtCore import Qt

import requests

from src.client.gui.theme import COLORS


class AuthDialog(QDialog):
    """Login / first-time GM setup dialog.

    mode='setup'  — only shows Register tab, role locked to 'gm'
    mode='login'  — only shows Login tab
    mode='both'   — shows both tabs (for future use)
    """

    def __init__(self, base_url: str, mode: str = "login", parent=None):
        super().__init__(parent)
        self.base_url = base_url
        self.mode = mode
        self.token: str | None = None
        self.user: dict | None = None

        self.setWindowTitle("DnD Tool — Anmeldung")
        self.setMinimumWidth(400)
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)

        self._build_ui()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        header = QLabel("⚔ DnD Tool")
        header.setStyleSheet(f"color: {COLORS['accent']}; font-size: 20px; font-weight: bold;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        if self.mode == "setup":
            layout.addWidget(self._make_info_label(
                "Willkommen! Erstelle zunächst deinen GM-Account."
            ))
            layout.addWidget(self._build_register_widget(gm_only=True))
        elif self.mode == "login":
            layout.addWidget(self._build_login_widget())
        else:
            tabs = QTabWidget()
            tabs.addTab(self._build_login_widget(), "Anmelden")
            tabs.addTab(self._build_register_widget(gm_only=False), "Registrieren")
            layout.addWidget(tabs)

    def _make_info_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {COLORS['subtext']}; font-size: 13px;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setWordWrap(True)
        return lbl

    def _build_login_widget(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(8)

        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Benutzername")

        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Passwort")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)

        form.addRow("Benutzer:", self.login_username)
        form.addRow("Passwort:", self.login_password)
        layout.addLayout(form)

        self.login_error = QLabel("")
        self.login_error.setStyleSheet(f"color: {COLORS['error']}; font-size: 12px;")
        self.login_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.login_error)

        btn = QPushButton("Anmelden")
        btn.setObjectName("primary-btn")
        btn.clicked.connect(self._do_login)
        self.login_password.returnPressed.connect(self._do_login)
        layout.addWidget(btn)

        return w

    def _build_register_widget(self, gm_only: bool) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(8)

        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText("Benutzername (3–50 Zeichen)")

        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("Passwort (min. 6 Zeichen)")
        self.reg_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.reg_password2 = QLineEdit()
        self.reg_password2.setPlaceholderText("Passwort wiederholen")
        self.reg_password2.setEchoMode(QLineEdit.EchoMode.Password)

        form.addRow("Benutzer:", self.reg_username)
        form.addRow("Passwort:", self.reg_password)
        form.addRow("Wiederholen:", self.reg_password2)

        self._gm_only = gm_only
        if gm_only:
            role_lbl = QLabel("Rolle:  Game Master (fest)")
            role_lbl.setStyleSheet(f"color: {COLORS['muted']}; font-size: 12px;")
            form.addRow("", role_lbl)

        layout.addLayout(form)

        self.reg_error = QLabel("")
        self.reg_error.setStyleSheet(f"color: {COLORS['error']}; font-size: 12px;")
        self.reg_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.reg_error)

        label = "GM-Account erstellen" if gm_only else "Registrieren"
        btn = QPushButton(label)
        btn.setObjectName("primary-btn")
        btn.clicked.connect(self._do_register)
        layout.addWidget(btn)

        return w

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _do_login(self) -> None:
        username = self.login_username.text().strip()
        password = self.login_password.text()
        self.login_error.setText("")

        if not username or not password:
            self.login_error.setText("Bitte alle Felder ausfüllen.")
            return

        try:
            r = requests.post(
                f"{self.base_url}/api/auth/login",
                json={"username": username, "password": password},
                timeout=5,
            )
            data = r.json()
            if r.status_code == 200:
                self.token = data["token"]
                self.user = data["user"]
                self.accept()
            else:
                self.login_error.setText(data.get("error", "Anmeldung fehlgeschlagen."))
        except Exception as e:
            self.login_error.setText(f"Verbindungsfehler: {e}")

    def _do_register(self) -> None:
        username = self.reg_username.text().strip()
        password = self.reg_password.text()
        password2 = self.reg_password2.text()
        self.reg_error.setText("")

        if not username or not password or not password2:
            self.reg_error.setText("Bitte alle Felder ausfüllen.")
            return
        if password != password2:
            self.reg_error.setText("Passwörter stimmen nicht überein.")
            return

        role = "gm" if self._gm_only else "player"

        try:
            r = requests.post(
                f"{self.base_url}/api/auth/register",
                json={"username": username, "password": password, "role": role},
                timeout=5,
            )
            data = r.json()
            if r.status_code == 201:
                self.token = data["token"]
                self.user = data["user"]
                self.accept()
            else:
                self.reg_error.setText(data.get("error", "Registrierung fehlgeschlagen."))
        except Exception as e:
            self.reg_error.setText(f"Verbindungsfehler: {e}")
