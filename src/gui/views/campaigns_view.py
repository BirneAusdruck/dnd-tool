"""
Campaign list view — shows all campaigns with edit/delete actions.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QInputDialog, QMessageBox, QSizePolicy,
)
from PySide6.QtCore import Qt

import requests

from src.gui.theme import COLORS

_HDR = f"color:{COLORS['accent']};font-size:22px;font-weight:bold;"


class CampaignsView(QWidget):
    def __init__(self, base_url: str, parent=None):
        super().__init__(parent)
        self._base_url    = base_url
        self._auth_token: str | None = None
        self._build_ui()

    def set_auth(self, token: str | None) -> None:
        self._auth_token = token
        self._load()

    # ── UI ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Top bar
        top = QWidget()
        top.setStyleSheet(
            f"background:{COLORS['sidebar']};border-bottom:1px solid {COLORS['border']};"
        )
        top.setFixedHeight(56)
        top_l = QHBoxLayout(top)
        top_l.setContentsMargins(24, 0, 24, 0)

        lbl = QLabel("Kampagnen")
        lbl.setStyleSheet(_HDR)
        btn_new = QPushButton("+ Neue Kampagne")
        btn_new.setObjectName("primary-btn")
        btn_new.setFixedHeight(34)
        btn_new.clicked.connect(self._new_campaign)

        top_l.addWidget(lbl)
        top_l.addStretch()
        top_l.addWidget(btn_new)
        outer.addWidget(top)

        # Scroll area for cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            f"QScrollArea{{border:none;background:{COLORS['bg']};}}"
        )
        self._cards_widget = QWidget()
        self._cards_widget.setStyleSheet(f"background:{COLORS['bg']};")
        self._cards_layout = QVBoxLayout(self._cards_widget)
        self._cards_layout.setContentsMargins(24, 24, 24, 24)
        self._cards_layout.setSpacing(12)
        self._cards_layout.addStretch()
        scroll.setWidget(self._cards_widget)
        outer.addWidget(scroll, 1)

    # ── Data ─────────────────────────────────────────────────────────────

    def _load(self):
        # Clear old cards (keep stretch)
        while self._cards_layout.count() > 1:
            item = self._cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self._auth_token:
            return

        try:
            r = requests.get(
                f"{self._base_url}/api/campaigns/",
                headers={"Authorization": f"Bearer {self._auth_token}"},
                timeout=4,
            )
            if r.ok:
                for c in r.json():
                    self._cards_layout.insertWidget(
                        self._cards_layout.count() - 1,
                        _CampaignCard(c, self._base_url, self._auth_token,
                                      on_delete=self._load)
                    )
        except Exception:
            pass

    def _new_campaign(self):
        name, ok = QInputDialog.getText(
            self, "Neue Kampagne", "Kampagnenname:"
        )
        if not ok or not name.strip():
            return
        try:
            r = requests.post(
                f"{self._base_url}/api/campaigns/",
                json={"name": name.strip()},
                headers={"Authorization": f"Bearer {self._auth_token}"},
                timeout=4,
            )
            if r.ok:
                self._open_editor(r.json())
                self._load()
            else:
                QMessageBox.warning(self, "Fehler", r.json().get("error", "Unbekannt"))
        except Exception as e:
            QMessageBox.warning(self, "Fehler", str(e))

    def _open_editor(self, campaign_data: dict):
        from src.gui.dialogs.campaign_editor import CampaignEditor
        dlg = CampaignEditor(
            campaign_data, self._base_url, self._auth_token, parent=self
        )
        dlg.exec()
        self._load()


class _CampaignCard(QFrame):
    def __init__(self, data: dict, base_url: str, token: str,
                 on_delete, parent=None):
        super().__init__(parent)
        self._data     = data
        self._base_url = base_url
        self._token    = token
        self._on_delete = on_delete
        self._build()

    def _build(self):
        self.setStyleSheet(
            f"QFrame{{background:{COLORS['surface']};border-radius:8px;"
            f"border:1px solid {COLORS['border']};}}"
        )
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        row = QHBoxLayout(self)
        row.setContentsMargins(16, 12, 16, 12)
        row.setSpacing(16)

        # Info
        info = QVBoxLayout()
        name = QLabel(self._data["name"])
        name.setStyleSheet(
            f"color:{COLORS['text']};font-size:15px;font-weight:bold;"
        )
        meta = QLabel(
            f"📖 {self._data.get('chapter_count', 0)} Kapitel  "
            f"👤 {self._data.get('npc_count', 0)} NSC  "
            f"⚔ {self._data.get('encounter_count', 0)} Begegnungen  "
            f"🔑 {self._data['join_code']}"
        )
        meta.setStyleSheet(f"color:{COLORS['muted']};font-size:11px;")
        info.addWidget(name)
        info.addWidget(meta)
        row.addLayout(info, 1)

        # Buttons
        btn_open = QPushButton("Öffnen")
        btn_open.setObjectName("primary-btn")
        btn_open.setFixedWidth(90)
        btn_open.clicked.connect(self._open)

        btn_del = QPushButton("Löschen")
        btn_del.setObjectName("secondary-btn")
        btn_del.setFixedWidth(80)
        btn_del.clicked.connect(self._delete)

        row.addWidget(btn_open)
        row.addWidget(btn_del)

    def _open(self):
        try:
            r = requests.get(
                f"{self._base_url}/api/campaigns/{self._data['id']}",
                headers={"Authorization": f"Bearer {self._token}"},
                timeout=4,
            )
            if r.ok:
                from src.gui.dialogs.campaign_editor import CampaignEditor
                dlg = CampaignEditor(
                    r.json(), self._base_url, self._token, parent=self
                )
                dlg.exec()
                self._on_delete()  # refresh
        except Exception as e:
            QMessageBox.warning(self, "Fehler", str(e))

    def _delete(self):
        if QMessageBox.question(
            self, "Löschen",
            f'Kampagne "{self._data["name"]}" wirklich löschen?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        ) != QMessageBox.StandardButton.Yes:
            return
        try:
            requests.delete(
                f"{self._base_url}/api/campaigns/{self._data['id']}",
                headers={"Authorization": f"Bearer {self._token}"},
                timeout=4,
            )
        except Exception:
            pass
        self._on_delete()
