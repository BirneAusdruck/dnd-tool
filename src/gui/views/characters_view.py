from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QMessageBox, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal

import requests

from src.gui.theme import COLORS
from src.game.srd_loader import get_race, get_class, get_background


class _CharacterCard(QFrame):
    open_sheet = Signal(dict)
    delete_char = Signal(int)

    def __init__(self, char: dict, parent=None):
        super().__init__(parent)
        self.char = char
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(
            f"QFrame{{background:{COLORS['surface']};border:1px solid {COLORS['border']};border-radius:8px;}}"
        )
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._build()

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        data = self.char.get("data", {})
        basics = data.get("basics", {})
        scores = data.get("ability_scores", {})

        race_name = get_race(basics.get("race", ""))
        race_name = race_name["name"] if race_name else basics.get("race", "?")
        cls_name = get_class(basics.get("class", ""))
        cls_name = cls_name["name"] if cls_name else basics.get("class", "?")
        level = basics.get("level", 1)

        # Left: name + subtitle
        left = QVBoxLayout()
        name_lbl = QLabel(self.char.get("name", "?"))
        name_lbl.setStyleSheet(f"font-size:16px;font-weight:bold;color:{COLORS['text']};")
        sub_lbl = QLabel(f"Level {level} {race_name} {cls_name}")
        sub_lbl.setStyleSheet(f"color:{COLORS['subtext']};font-size:12px;")
        left.addWidget(name_lbl)
        left.addWidget(sub_lbl)
        layout.addLayout(left, 1)

        # Middle: quick stats
        hp = data.get("hp", {})
        mid = QLabel(f"HP {hp.get('current',0)}/{hp.get('max',0)}")
        mid.setStyleSheet(f"color:{COLORS['success']};font-size:13px;font-weight:bold;")
        layout.addWidget(mid)

        layout.addSpacing(16)

        # Buttons
        btn_open = QPushButton("Charakter-Bogen")
        btn_open.setObjectName("secondary-btn")
        btn_open.setFixedWidth(140)
        btn_open.clicked.connect(lambda: self.open_sheet.emit(self.char))

        btn_del = QPushButton("Löschen")
        btn_del.setObjectName("secondary-btn")
        btn_del.setFixedWidth(80)
        btn_del.setStyleSheet(f"QPushButton{{color:{COLORS['error']};background:{COLORS['surface']};border:1px solid {COLORS['error']};border-radius:6px;padding:6px;}}")
        btn_del.clicked.connect(lambda: self.delete_char.emit(self.char["id"]))

        layout.addWidget(btn_open)
        layout.addWidget(btn_del)


class CharactersView(QWidget):
    open_sheet_requested = Signal(dict)

    def __init__(self, base_url: str, parent=None):
        super().__init__(parent)
        self.base_url = base_url
        self._auth_token: str | None = None
        self._build_ui()

    def set_auth(self, token: str | None) -> None:
        self._auth_token = token
        if token:
            self.refresh()

    # ------------------------------------------------------------------

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(16)

        # Header row
        header = QHBoxLayout()
        title = QLabel("Charaktere")
        title.setObjectName("title")
        header.addWidget(title)
        header.addStretch()

        btn_new = QPushButton("+ Neuer Charakter")
        btn_new.setObjectName("primary-btn")
        btn_new.clicked.connect(self._new_character)
        header.addWidget(btn_new)
        outer.addLayout(header)

        # Scroll area for cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self._cards_container = QWidget()
        self._cards_layout = QVBoxLayout(self._cards_container)
        self._cards_layout.setSpacing(10)
        self._cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._empty_lbl = QLabel("Noch keine Charaktere erstellt.")
        self._empty_lbl.setStyleSheet(f"color:{COLORS['muted']};font-style:italic;")
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._cards_layout.addWidget(self._empty_lbl)

        scroll.setWidget(self._cards_container)
        outer.addWidget(scroll, 1)

    # ------------------------------------------------------------------

    def refresh(self):
        if not self._auth_token:
            return
        try:
            r = requests.get(
                f"{self.base_url}/api/characters/",
                headers={"Authorization": f"Bearer {self._auth_token}"},
                timeout=3,
            )
            if r.status_code == 200:
                self._populate(r.json())
        except Exception:
            pass

    def _populate(self, chars: list[dict]):
        while self._cards_layout.count():
            item = self._cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not chars:
            lbl = QLabel("Noch keine Charaktere erstellt.")
            lbl.setStyleSheet(f"color:{COLORS['muted']};font-style:italic;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._cards_layout.addWidget(lbl)
            return

        for char in chars:
            card = _CharacterCard(char)
            card.open_sheet.connect(self.open_sheet_requested)
            card.delete_char.connect(self._confirm_delete)
            self._cards_layout.addWidget(card)

    def _new_character(self):
        from src.gui.dialogs.character_wizard import CharacterWizard
        dlg = CharacterWizard(self.base_url, self._auth_token, parent=self)
        if dlg.exec():
            self.refresh()

    def _confirm_delete(self, char_id: int):
        resp = QMessageBox.question(
            self, "Charakter löschen",
            "Charakter wirklich löschen? Dies kann nicht rückgängig gemacht werden.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resp != QMessageBox.StandardButton.Yes:
            return
        try:
            requests.delete(
                f"{self.base_url}/api/characters/{char_id}",
                headers={"Authorization": f"Bearer {self._auth_token}"},
                timeout=3,
            )
            self.refresh()
        except Exception as e:
            QMessageBox.warning(self, "Fehler", str(e))
