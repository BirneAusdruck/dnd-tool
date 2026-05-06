"""
Dialog zum Hinzufügen eines Tokens auf die VTT-Karte.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QSpinBox, QPushButton, QButtonGroup, QWidget,
    QToolButton, QFrame, QScrollArea,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

import requests

from src.gui.theme import COLORS
from src.gui.widgets.token_item import TokenItem, TOKEN_COLORS, SIZE_LABELS


class TokenDialog(QDialog):
    """Modal dialog for creating a new VTT token."""

    def __init__(self, auth_token: str | None, base_url: str, parent=None):
        super().__init__(parent)
        self._auth_token = auth_token
        self._base_url = base_url
        self._selected_color = TOKEN_COLORS[0]
        self._color_buttons: list[QToolButton] = []
        self._result: dict | None = None

        self.setWindowTitle("Token hinzufügen")
        self.setMinimumWidth(380)
        self.setStyleSheet(
            f"background:{COLORS['bg']};color:{COLORS['text']};"
            f"QLabel{{color:{COLORS['text']};font-size:12px;}}"
            f"QLineEdit,QComboBox,QSpinBox{{background:{COLORS['surface']};"
            f"color:{COLORS['text']};border:1px solid {COLORS['border']};"
            f"border-radius:4px;padding:4px 6px;font-size:12px;}}"
        )

        self._build_ui()
        self._load_characters()

    # ── UI ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        layout.addWidget(self._section("Name"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("z. B. Goblin 1 / Thalindra")
        layout.addWidget(self.name_edit)

        layout.addWidget(self._section("Farbe"))
        layout.addWidget(self._build_color_row())

        layout.addWidget(self._section("Größe"))
        self.size_combo = QComboBox()
        self.size_combo.addItems(SIZE_LABELS)
        self.size_combo.setCurrentIndex(SIZE_LABELS.index("medium"))
        layout.addWidget(self.size_combo)

        layout.addWidget(self._section("HP Maximum"))
        self.hp_spin = QSpinBox()
        self.hp_spin.setRange(1, 9999)
        self.hp_spin.setValue(10)
        layout.addWidget(self.hp_spin)

        layout.addWidget(self._section("Charakter verknüpfen (optional)"))
        self.char_combo = QComboBox()
        self.char_combo.addItem("— keiner —", None)
        self.char_combo.currentIndexChanged.connect(self._on_char_selected)
        layout.addWidget(self.char_combo)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color:{COLORS['border']};")
        layout.addWidget(sep)

        # Buttons
        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Abbrechen")
        btn_cancel.setObjectName("secondary-btn")
        btn_cancel.clicked.connect(self.reject)
        btn_ok = QPushButton("Hinzufügen")
        btn_ok.setObjectName("primary-btn")
        btn_ok.clicked.connect(self._accept)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

    def _section(self, title: str) -> QLabel:
        lbl = QLabel(title)
        lbl.setStyleSheet(f"color:{COLORS['muted']};font-size:11px;font-weight:bold;")
        return lbl

    def _build_color_row(self) -> QWidget:
        container = QWidget()
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(4)

        group = QButtonGroup(self)
        group.setExclusive(True)

        for color in TOKEN_COLORS:
            btn = QToolButton()
            btn.setCheckable(True)
            btn.setFixedSize(28, 28)
            btn.setStyleSheet(
                f"QToolButton{{background:{color};border:2px solid transparent;border-radius:14px;}}"
                f"QToolButton:checked{{border:2px solid white;}}"
            )
            btn.clicked.connect(lambda checked, c=color: self._select_color(c))
            group.addButton(btn)
            row.addWidget(btn)
            self._color_buttons.append(btn)

        self._color_buttons[0].setChecked(True)
        row.addStretch()
        return container

    # ── Data ──────────────────────────────────────────────────────────────

    def _load_characters(self):
        if not self._auth_token:
            return
        try:
            r = requests.get(
                f"{self._base_url}/api/characters/",
                headers={"Authorization": f"Bearer {self._auth_token}"},
                timeout=3,
            )
            if r.ok:
                for ch in r.json():
                    data = ch.get("data", {})
                    label = f"{ch['name']} ({data.get('class', '')} {data.get('level', 1)})"
                    self.char_combo.addItem(label, ch["id"])
        except Exception:
            pass

    def _on_char_selected(self, index: int):
        char_id = self.char_combo.currentData()
        if char_id is None:
            return
        try:
            r = requests.get(
                f"{self._base_url}/api/characters/{char_id}",
                headers={"Authorization": f"Bearer {self._auth_token}"},
                timeout=3,
            )
            if r.ok:
                ch = r.json()
                data = ch.get("data", {})
                if not self.name_edit.text().strip():
                    self.name_edit.setText(ch["name"])
                hp_max = data.get("hp_max", 10)
                self.hp_spin.setValue(hp_max)
        except Exception:
            pass

    def _select_color(self, color: str):
        self._selected_color = color

    def _accept(self):
        name = self.name_edit.text().strip()
        if not name:
            self.name_edit.setFocus()
            return
        self._result = {
            "token_id": TokenItem.new_id(),
            "name": name,
            "color": self._selected_color,
            "size": self.size_combo.currentText(),
            "hp_max": self.hp_spin.value(),
            "char_id": self.char_combo.currentData(),
        }
        self.accept()

    def result_data(self) -> dict:
        return self._result or {}
