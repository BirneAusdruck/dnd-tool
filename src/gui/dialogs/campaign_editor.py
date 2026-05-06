"""
Campaign Editor – vollständiger Editor für Kampagnen.

Tabs:
  Geschichte        – Kapitel/Szenen-Baum + Szeneneditor
  NSC               – NPC-Liste + Formular
  Gegenstände       – Item-Liste + Formular
  Begegnungen       – Encounter-Liste + Formular
  Flags & Entsch.   – Flag-Tracking + Entscheidungsbäume

Flag-System:
  Jeder Flag hat einen Namen und is_set-Status (Spieler haben es getan?).
  Szenen können Flags *benötigen* oder *setzen*.
  Der Szenen-Baum zeigt Szenen mit nicht erfüllten Flags orange.
"""
from __future__ import annotations
import secrets
from typing import Any

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QTreeWidget, QTreeWidgetItem,
    QListWidget, QListWidgetItem, QLabel, QLineEdit, QTextEdit, QComboBox,
    QSpinBox, QPushButton, QTabWidget, QWidget, QFrame, QCheckBox,
    QScrollArea, QSizePolicy, QMessageBox, QInputDialog, QGroupBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont

import requests

from src.gui.theme import COLORS

# ── helpers ───────────────────────────────────────────────────────────────

def _uid() -> str:
    return secrets.token_hex(6)


def _lbl(text: str, muted: bool = False) -> QLabel:
    lbl = QLabel(text)
    color = COLORS["muted"] if muted else COLORS["text"]
    lbl.setStyleSheet(f"color:{color};font-size:12px;")
    return lbl


def _edit(placeholder: str = "") -> QLineEdit:
    w = QLineEdit()
    w.setPlaceholderText(placeholder)
    w.setStyleSheet(
        f"background:{COLORS['surface']};color:{COLORS['text']};"
        f"border:1px solid {COLORS['border']};border-radius:4px;padding:4px 6px;"
    )
    return w


def _textedit(placeholder: str = "", height: int = 120) -> QTextEdit:
    w = QTextEdit()
    w.setPlaceholderText(placeholder)
    w.setMinimumHeight(height)
    w.setStyleSheet(
        f"background:{COLORS['surface']};color:{COLORS['text']};"
        f"border:1px solid {COLORS['border']};border-radius:4px;padding:4px;"
    )
    return w


def _combo(items: list[str]) -> QComboBox:
    w = QComboBox()
    w.addItems(items)
    w.setStyleSheet(
        f"background:{COLORS['surface']};color:{COLORS['text']};"
        f"border:1px solid {COLORS['border']};border-radius:4px;padding:4px;"
    )
    return w


def _btn(label: str, obj_name: str = "secondary-btn", w: int = 0) -> QPushButton:
    b = QPushButton(label)
    b.setObjectName(obj_name)
    b.setFixedHeight(30)
    if w:
        b.setFixedWidth(w)
    return b


def _section(title: str) -> QLabel:
    lbl = QLabel(title)
    lbl.setStyleSheet(
        f"color:{COLORS['muted']};font-size:10px;font-weight:bold;"
        f"text-transform:uppercase;letter-spacing:1px;"
    )
    return lbl


def _sep() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet(f"color:{COLORS['border']};")
    return f


ITEM_TYPES    = ["Waffe", "Rüstung", "Wundersam", "Werkzeug", "Konsumierbar", "Sonstiges"]
RARITIES      = ["Gewöhnlich", "Ungewöhnlich", "Selten", "Sehr selten", "Legendär", "Artefakt"]
DIFFICULTIES  = ["Leicht", "Mittel", "Schwer", "Tödlich"]
SKILLS        = [
    "Akrobatik", "Arkanes", "Athletik", "Auftreten", "Einschüchtern",
    "Geschichte", "Heimlichkeit", "Medizin", "Natur", "Täuschen",
    "Tierkunde", "Überzeugung", "Überleben", "Wahrnehmung", "Weisheit",
    "Fingerfertigkeit", "Nachforschung", "Religion",
]

# ═══════════════════════════════════════════════════════════════════════════
# Main Dialog
# ═══════════════════════════════════════════════════════════════════════════

class CampaignEditor(QDialog):
    def __init__(self, campaign: dict, base_url: str, auth_token: str, parent=None):
        super().__init__(parent)
        self._campaign  = campaign
        self._base_url  = base_url
        self._token     = auth_token
        self._content   = campaign.get("content") or {
            "chapters": [], "npcs": [], "items": [],
            "encounters": [], "flags": [],
        }
        # Current selection state
        self._cur_scene_ids: tuple[str, str] | None = None  # (chapter_id, scene_id)
        self._cur_npc_id:    str | None = None
        self._cur_item_id:   str | None = None
        self._cur_enc_id:    str | None = None

        self.setWindowTitle(f"Kampagnen-Editor — {campaign['name']}")
        self.resize(1300, 850)
        self.setStyleSheet(f"background:{COLORS['bg']};color:{COLORS['text']};")
        self._build_ui()

    # ── UI shell ─────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Top bar
        root.addWidget(self._top_bar())

        # Tab widget
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet(
            f"QTabWidget::pane{{border:none;background:{COLORS['bg']};}}"
            f"QTabBar::tab{{background:{COLORS['sidebar']};color:{COLORS['muted']};"
            f"padding:8px 18px;border:none;}}"
            f"QTabBar::tab:selected{{background:{COLORS['bg']};color:{COLORS['text']};"
            f"font-weight:bold;border-bottom:2px solid {COLORS['accent']};}}"
        )
        self._tabs.addTab(self._story_tab(),     "📖 Geschichte")
        self._tabs.addTab(self._npc_tab(),       "👤 NSC")
        self._tabs.addTab(self._item_tab(),      "🗡 Gegenstände")
        self._tabs.addTab(self._encounter_tab(), "⚔ Begegnungen")
        self._tabs.addTab(self._flags_tab(),     "🚩 Flags & Entscheidungen")
        root.addWidget(self._tabs, 1)

    def _top_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(52)
        bar.setStyleSheet(
            f"background:{COLORS['sidebar']};border-bottom:1px solid {COLORS['border']};"
        )
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 0, 16, 0)

        self._name_edit = QLineEdit(self._campaign["name"])
        self._name_edit.setStyleSheet(
            f"background:transparent;color:{COLORS['text']};font-size:16px;"
            f"font-weight:bold;border:none;border-bottom:1px solid {COLORS['border']};"
        )
        self._name_edit.setFixedWidth(340)

        btn_save = _btn("💾 Speichern", "primary-btn", 130)
        btn_save.clicked.connect(self._save)
        btn_close = _btn("Schließen", "secondary-btn", 100)
        btn_close.clicked.connect(self.accept)

        layout.addWidget(_lbl("Kampagne: ", True))
        layout.addWidget(self._name_edit)
        layout.addStretch()
        layout.addWidget(btn_save)
        layout.addWidget(btn_close)
        return bar

    # ═══════════════════════════════════════════════════════════════════════
    # TAB 1 – Geschichte
    # ═══════════════════════════════════════════════════════════════════════

    def _story_tab(self) -> QWidget:
        tab = QWidget()
        sp = QSplitter(Qt.Orientation.Horizontal, tab)
        sp.setStyleSheet(
            f"QSplitter::handle{{background:{COLORS['border']};width:1px;}}"
        )
        lay = QHBoxLayout(tab)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(sp)

        # ── Left: Chapter / Scene navigator ──────────────────────────────
        left = QWidget()
        left.setMinimumWidth(240)
        left.setMaximumWidth(320)
        left.setStyleSheet(f"background:{COLORS['sidebar']};")
        ll = QVBoxLayout(left)
        ll.setContentsMargins(8, 8, 8, 8)
        ll.setSpacing(4)

        ll.addWidget(_section("Struktur"))

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setStyleSheet(
            f"QTreeWidget{{background:{COLORS['sidebar']};color:{COLORS['text']};"
            f"border:none;font-size:12px;}}"
            f"QTreeWidget::item:selected{{background:{COLORS['surface']};}}"
        )
        self._tree.currentItemChanged.connect(self._on_tree_select)
        ll.addWidget(self._tree, 1)

        btn_row = QHBoxLayout()
        btn_ch  = _btn("+ Kapitel",  "primary-btn")
        btn_sc  = _btn("+ Szene",    "secondary-btn")
        btn_del = _btn("−",          "secondary-btn", 32)
        btn_ch.clicked.connect(self._add_chapter)
        btn_sc.clicked.connect(self._add_scene)
        btn_del.clicked.connect(self._del_tree_item)
        btn_row.addWidget(btn_ch)
        btn_row.addWidget(btn_sc)
        btn_row.addWidget(btn_del)
        ll.addLayout(btn_row)
        sp.addWidget(left)

        # ── Right: Scene editor ───────────────────────────────────────────
        self._scene_stack = QTabWidget()
        self._scene_stack.setStyleSheet(self._tabs.styleSheet())

        self._scene_empty = QWidget()
        el = QVBoxLayout(self._scene_empty)
        el.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint = QLabel("← Szene auswählen oder erstellen")
        hint.setStyleSheet(f"color:{COLORS['muted']};font-size:14px;")
        el.addWidget(hint)

        # Scene editor inner tabs
        self._se_title    = _edit("Szenen-Titel")
        self._se_content  = _textedit("Geschichte / Beschreibung …", 200)
        self._se_notes    = _textedit("GM-Notizen (nicht für Spieler) …", 100)

        # Flag banner (at top of scene editor)
        self._flag_banner = QLabel("")
        self._flag_banner.setWordWrap(True)
        self._flag_banner.setStyleSheet(
            f"color:{COLORS['warning'] if 'warning' in COLORS else COLORS['gold']};"
            f"font-size:11px;padding:4px 8px;"
            f"background:{COLORS['surface']};border-radius:4px;"
        )
        self._flag_banner.setVisible(False)

        scene_editor = QWidget()
        sel = QVBoxLayout(scene_editor)
        sel.setContentsMargins(12, 8, 12, 8)
        sel.setSpacing(6)
        sel.addWidget(_lbl("Titel:", True))
        sel.addWidget(self._se_title)
        sel.addWidget(self._flag_banner)

        inner_tabs = QTabWidget()
        inner_tabs.setStyleSheet(self._tabs.styleSheet())

        # Geschichte tab
        gt = QWidget()
        gl = QVBoxLayout(gt)
        gl.setContentsMargins(8, 8, 8, 8)
        gl.addWidget(self._se_content)
        inner_tabs.addTab(gt, "Geschichte")

        # Verknüpfungen tab
        inner_tabs.addTab(self._build_links_tab(), "Verknüpfungen")

        # Entscheidungen tab
        inner_tabs.addTab(self._build_decisions_tab(), "Entscheidungen")

        # Skill Checks tab
        inner_tabs.addTab(self._build_skill_checks_tab(), "Skill Checks")

        # Flags tab
        inner_tabs.addTab(self._build_scene_flags_tab(), "Flags")

        # Notizen tab
        nt = QWidget()
        nl = QVBoxLayout(nt)
        nl.setContentsMargins(8, 8, 8, 8)
        nl.addWidget(self._se_notes)
        inner_tabs.addTab(nt, "GM-Notizen")

        sel.addWidget(inner_tabs, 1)

        self._scene_stack.addTab(self._scene_empty, "—")
        self._scene_stack.addTab(scene_editor, "Szene")
        self._scene_stack.setCurrentIndex(0)
        self._scene_stack.tabBar().setVisible(False)
        sp.addWidget(self._scene_stack)
        sp.setSizes([270, 1000])

        self._populate_tree()
        return tab

    def _build_links_tab(self) -> QWidget:
        w = QScrollArea()
        w.setWidgetResizable(True)
        w.setStyleSheet(f"QScrollArea{{border:none;background:{COLORS['bg']};}}")
        inner = QWidget()
        inner.setStyleSheet(f"background:{COLORS['bg']};")
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(12)

        self._link_npcs  = self._build_check_list("Verknüpfte NSC")
        self._link_items = self._build_check_list("Verknüpfte Gegenstände")
        self._link_encs  = self._build_check_list("Verknüpfte Begegnungen")

        lay.addWidget(self._link_npcs[0])
        lay.addWidget(self._link_items[0])
        lay.addWidget(self._link_encs[0])
        lay.addStretch()
        w.setWidget(inner)
        return w

    def _build_check_list(self, title: str) -> tuple[QGroupBox, QListWidget]:
        grp = QGroupBox(title)
        grp.setStyleSheet(
            f"QGroupBox{{color:{COLORS['muted']};font-size:11px;font-weight:bold;"
            f"border:1px solid {COLORS['border']};border-radius:4px;padding-top:12px;"
            f"margin-top:6px;}}"
        )
        gl = QVBoxLayout(grp)
        lw = QListWidget()
        lw.setStyleSheet(
            f"QListWidget{{background:{COLORS['surface']};border:none;font-size:12px;}}"
        )
        lw.setMaximumHeight(120)
        gl.addWidget(lw)
        return grp, lw

    def _build_decisions_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(6)

        lay.addWidget(_section("Entscheidungspunkte in dieser Szene"))

        self._dec_list = QListWidget()
        self._dec_list.setStyleSheet(
            f"QListWidget{{background:{COLORS['surface']};border:1px solid {COLORS['border']};"
            f"border-radius:4px;font-size:12px;}}"
        )
        self._dec_list.currentRowChanged.connect(self._on_dec_select)
        lay.addWidget(self._dec_list, 1)

        dec_btns = QHBoxLayout()
        b_add = _btn("+ Entscheidung", "primary-btn")
        b_del = _btn("− Entfernen",    "secondary-btn")
        b_add.clicked.connect(self._add_decision)
        b_del.clicked.connect(self._del_decision)
        dec_btns.addWidget(b_add)
        dec_btns.addWidget(b_del)
        lay.addLayout(dec_btns)

        lay.addWidget(_sep())
        lay.addWidget(_section("Gewählte Entscheidung"))

        self._dec_desc = _edit("Frage / Beschreibung der Entscheidung")
        lay.addWidget(self._dec_desc)

        # Options
        lay.addWidget(_lbl("Optionen:", True))
        self._dec_options_layout = QVBoxLayout()
        lay.addLayout(self._dec_options_layout)

        b_opt = _btn("+ Option hinzufügen", "secondary-btn")
        b_opt.clicked.connect(self._add_option_row)
        lay.addWidget(b_opt)
        lay.addStretch()
        return w

    def _build_skill_checks_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(6)

        lay.addWidget(_section("Skill Checks in dieser Szene"))

        self._sc_list = QListWidget()
        self._sc_list.setStyleSheet(
            f"QListWidget{{background:{COLORS['surface']};border:1px solid {COLORS['border']};"
            f"border-radius:4px;font-size:12px;}}"
        )
        self._sc_list.currentRowChanged.connect(self._on_sc_select)
        lay.addWidget(self._sc_list, 1)

        sc_btns = QHBoxLayout()
        b_add = _btn("+ Skill Check", "primary-btn")
        b_del = _btn("− Entfernen",   "secondary-btn")
        b_add.clicked.connect(self._add_skill_check)
        b_del.clicked.connect(self._del_skill_check)
        sc_btns.addWidget(b_add)
        sc_btns.addWidget(b_del)
        lay.addLayout(sc_btns)

        lay.addWidget(_sep())
        lay.addWidget(_section("Details"))
        form = QHBoxLayout()
        self._sc_skill = _combo(SKILLS)
        self._sc_dc    = QSpinBox()
        self._sc_dc.setRange(1, 30)
        self._sc_dc.setValue(12)
        self._sc_dc.setStyleSheet(
            f"background:{COLORS['surface']};color:{COLORS['text']};"
            f"border:1px solid {COLORS['border']};border-radius:4px;"
        )
        form.addWidget(_lbl("Fertigkeit:", True))
        form.addWidget(self._sc_skill)
        form.addWidget(_lbl("SG:", True))
        form.addWidget(self._sc_dc)
        form.addStretch()
        lay.addLayout(form)

        self._sc_success = _textedit("Erfolg: Was passiert?", 60)
        self._sc_failure = _textedit("Misserfolg: Was passiert?", 60)
        lay.addWidget(_lbl("Erfolg:", True))
        lay.addWidget(self._sc_success)
        lay.addWidget(_lbl("Misserfolg:", True))
        lay.addWidget(self._sc_failure)
        lay.addStretch()
        return w

    def _build_scene_flags_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(10)

        lay.addWidget(_section("Diese Szene benötigt folgende Flags (Spieler müssen diese Aktionen getan haben)"))
        self._flag_req_list = QListWidget()
        self._flag_req_list.setStyleSheet(
            f"QListWidget{{background:{COLORS['surface']};border:1px solid {COLORS['border']};"
            f"border-radius:4px;font-size:12px;}}"
        )
        self._flag_req_list.setMaximumHeight(140)
        lay.addWidget(self._flag_req_list)

        lay.addWidget(_sep())
        lay.addWidget(_section("Diese Szene setzt folgende Flags (wenn Spieler sie abschließen)"))
        self._flag_set_list = QListWidget()
        self._flag_set_list.setStyleSheet(
            f"QListWidget{{background:{COLORS['surface']};border:1px solid {COLORS['border']};"
            f"border-radius:4px;font-size:12px;}}"
        )
        self._flag_set_list.setMaximumHeight(140)
        lay.addWidget(self._flag_set_list)
        lay.addStretch()
        return w

    # ═══════════════════════════════════════════════════════════════════════
    # TAB 2 – NSC
    # ═══════════════════════════════════════════════════════════════════════

    def _npc_tab(self) -> QWidget:
        return self._entity_tab(
            entity_key="npcs",
            label_fn=lambda e: e.get("name", "?"),
            form_fn=self._npc_form,
            cur_id_attr="_cur_npc_id",
            load_fn=self._load_npc_form,
            collect_fn=self._collect_npc_form,
            list_attr="_npc_list",
        )

    def _item_tab(self) -> QWidget:
        return self._entity_tab(
            entity_key="items",
            label_fn=lambda e: e.get("name", "?"),
            form_fn=self._item_form,
            cur_id_attr="_cur_item_id",
            load_fn=self._load_item_form,
            collect_fn=self._collect_item_form,
            list_attr="_item_list",
        )

    def _encounter_tab(self) -> QWidget:
        return self._entity_tab(
            entity_key="encounters",
            label_fn=lambda e: e.get("name", "?"),
            form_fn=self._encounter_form,
            cur_id_attr="_cur_enc_id",
            load_fn=self._load_encounter_form,
            collect_fn=self._collect_encounter_form,
            list_attr="_enc_list",
        )

    def _entity_tab(self, entity_key, label_fn, form_fn, cur_id_attr,
                    load_fn, collect_fn, list_attr) -> QWidget:
        """Generic left-list / right-form pattern."""
        tab = QWidget()
        sp = QSplitter(Qt.Orientation.Horizontal, tab)
        sp.setStyleSheet(
            f"QSplitter::handle{{background:{COLORS['border']};width:1px;}}"
        )
        tl = QHBoxLayout(tab)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.addWidget(sp)

        # Left list
        left = QWidget()
        left.setMinimumWidth(200)
        left.setMaximumWidth(280)
        left.setStyleSheet(f"background:{COLORS['sidebar']};")
        ll = QVBoxLayout(left)
        ll.setContentsMargins(8, 8, 8, 8)
        lw = QListWidget()
        lw.setStyleSheet(
            f"QListWidget{{background:{COLORS['sidebar']};color:{COLORS['text']};"
            f"border:none;font-size:13px;}}"
            f"QListWidget::item:selected{{background:{COLORS['surface']};}}"
        )
        setattr(self, list_attr, lw)
        ll.addWidget(lw, 1)

        btn_row = QHBoxLayout()
        b_add = _btn("+ Neu", "primary-btn")
        b_del = _btn("− Löschen", "secondary-btn")
        btn_row.addWidget(b_add)
        btn_row.addWidget(b_del)
        ll.addLayout(btn_row)
        sp.addWidget(left)

        # Right form (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea{{border:none;background:{COLORS['bg']};}}")
        form_w = QWidget()
        form_w.setStyleSheet(f"background:{COLORS['bg']};")
        fl = QVBoxLayout(form_w)
        fl.setContentsMargins(16, 16, 16, 16)
        fl.setSpacing(8)
        form_fn(fl)
        fl.addStretch()
        scroll.setWidget(form_w)
        sp.addWidget(scroll)
        sp.setSizes([240, 900])

        # Wire up
        entities = self._content.get(entity_key, [])
        for e in entities:
            item = QListWidgetItem(label_fn(e))
            item.setData(Qt.ItemDataRole.UserRole, e["id"])
            lw.addItem(item)

        def _on_select(cur, prev):
            if prev:
                # Save previous
                prev_id = prev.data(Qt.ItemDataRole.UserRole)
                entity = self._find_entity(entity_key, prev_id)
                if entity:
                    collect_fn(entity)
                    prev.setText(label_fn(entity))
            if cur:
                setattr(self, cur_id_attr, cur.data(Qt.ItemDataRole.UserRole))
                entity = self._find_entity(entity_key, getattr(self, cur_id_attr))
                if entity:
                    load_fn(entity)
            else:
                setattr(self, cur_id_attr, None)

        lw.currentItemChanged.connect(_on_select)

        def _add():
            name, ok = QInputDialog.getText(self, "Neu", "Name:")
            if not ok or not name.strip():
                return
            e = {"id": _uid(), "name": name.strip()}
            self._content.setdefault(entity_key, []).append(e)
            item = QListWidgetItem(label_fn(e))
            item.setData(Qt.ItemDataRole.UserRole, e["id"])
            lw.addItem(item)
            lw.setCurrentItem(item)
            self._refresh_link_lists()

        def _del():
            row = lw.currentRow()
            if row < 0:
                return
            item = lw.item(row)
            eid = item.data(Qt.ItemDataRole.UserRole)
            self._content[entity_key] = [
                e for e in self._content.get(entity_key, []) if e["id"] != eid
            ]
            lw.takeItem(row)
            setattr(self, cur_id_attr, None)
            self._refresh_link_lists()

        b_add.clicked.connect(_add)
        b_del.clicked.connect(_del)

        # Select first
        if lw.count():
            lw.setCurrentRow(0)

        return tab

    # ── NPC form ──────────────────────────────────────────────────────────

    def _npc_form(self, lay: QVBoxLayout):
        lay.addWidget(_section("NSC"))
        self._npc_name  = _edit("Name")
        self._npc_race  = _edit("Rasse")
        self._npc_role  = _edit("Rolle / Beruf")
        self._npc_desc  = _textedit("Beschreibung / Aussehen …", 120)
        self._npc_notes = _textedit("GM-Notizen …", 80)
        for w, l in [(self._npc_name, "Name"), (self._npc_race, "Rasse"),
                     (self._npc_role, "Rolle")]:
            lay.addWidget(_lbl(l + ":", True))
            lay.addWidget(w)
        lay.addWidget(_lbl("Beschreibung:", True))
        lay.addWidget(self._npc_desc)
        lay.addWidget(_lbl("GM-Notizen:", True))
        lay.addWidget(self._npc_notes)

    def _load_npc_form(self, e: dict):
        self._npc_name.setText(e.get("name", ""))
        self._npc_race.setText(e.get("race", ""))
        self._npc_role.setText(e.get("role", ""))
        self._npc_desc.setPlainText(e.get("description", ""))
        self._npc_notes.setPlainText(e.get("notes", ""))

    def _collect_npc_form(self, e: dict):
        e["name"]        = self._npc_name.text().strip() or e.get("name", "NSC")
        e["race"]        = self._npc_race.text().strip()
        e["role"]        = self._npc_role.text().strip()
        e["description"] = self._npc_desc.toPlainText()
        e["notes"]       = self._npc_notes.toPlainText()

    # ── Item form ──────────────────────────────────────────────────────────

    def _item_form(self, lay: QVBoxLayout):
        lay.addWidget(_section("Gegenstand"))
        self._item_name    = _edit("Name")
        self._item_type    = _combo(ITEM_TYPES)
        self._item_rarity  = _combo(RARITIES)
        self._item_desc    = _textedit("Beschreibung …", 100)
        self._item_effects = _textedit("Effekte / Eigenschaften …", 80)
        lay.addWidget(_lbl("Name:", True))
        lay.addWidget(self._item_name)
        row = QHBoxLayout()
        row.addWidget(_lbl("Typ:", True))
        row.addWidget(self._item_type)
        row.addWidget(_lbl("Seltenheit:", True))
        row.addWidget(self._item_rarity)
        lay.addLayout(row)
        lay.addWidget(_lbl("Beschreibung:", True))
        lay.addWidget(self._item_desc)
        lay.addWidget(_lbl("Effekte:", True))
        lay.addWidget(self._item_effects)

    def _load_item_form(self, e: dict):
        self._item_name.setText(e.get("name", ""))
        idx = ITEM_TYPES.index(e.get("type", ITEM_TYPES[0])) if e.get("type") in ITEM_TYPES else 0
        self._item_type.setCurrentIndex(idx)
        idx2 = RARITIES.index(e.get("rarity", RARITIES[0])) if e.get("rarity") in RARITIES else 0
        self._item_rarity.setCurrentIndex(idx2)
        self._item_desc.setPlainText(e.get("description", ""))
        self._item_effects.setPlainText(e.get("effects", ""))

    def _collect_item_form(self, e: dict):
        e["name"]        = self._item_name.text().strip() or e.get("name", "Gegenstand")
        e["type"]        = self._item_type.currentText()
        e["rarity"]      = self._item_rarity.currentText()
        e["description"] = self._item_desc.toPlainText()
        e["effects"]     = self._item_effects.toPlainText()

    # ── Encounter form ────────────────────────────────────────────────────

    def _encounter_form(self, lay: QVBoxLayout):
        lay.addWidget(_section("Begegnung"))
        self._enc_name   = _edit("Name")
        self._enc_diff   = _combo(DIFFICULTIES)
        self._enc_xp     = QSpinBox()
        self._enc_xp.setRange(0, 999999)
        self._enc_xp.setSuffix(" XP")
        self._enc_xp.setStyleSheet(
            f"background:{COLORS['surface']};color:{COLORS['text']};"
            f"border:1px solid {COLORS['border']};border-radius:4px;"
        )
        self._enc_enemies = _textedit("Gegner (je Zeile: Name, Anzahl, HG)", 120)
        self._enc_notes   = _textedit("Taktik / GM-Notizen …", 80)

        lay.addWidget(_lbl("Name:", True))
        lay.addWidget(self._enc_name)
        row = QHBoxLayout()
        row.addWidget(_lbl("Schwierigkeit:", True))
        row.addWidget(self._enc_diff)
        row.addWidget(_lbl("Erfahrungspunkte:", True))
        row.addWidget(self._enc_xp)
        lay.addLayout(row)
        lay.addWidget(_lbl("Gegner (je Zeile: Name | Anzahl | HG):", True))
        lay.addWidget(self._enc_enemies)
        lay.addWidget(_lbl("GM-Notizen:", True))
        lay.addWidget(self._enc_notes)

    def _load_encounter_form(self, e: dict):
        self._enc_name.setText(e.get("name", ""))
        idx = DIFFICULTIES.index(e.get("difficulty", DIFFICULTIES[0])) if e.get("difficulty") in DIFFICULTIES else 1
        self._enc_diff.setCurrentIndex(idx)
        self._enc_xp.setValue(e.get("xp", 0))
        enemies = e.get("enemies", [])
        if isinstance(enemies, list):
            self._enc_enemies.setPlainText(
                "\n".join(f"{en.get('name','?')} | {en.get('count',1)} | HG {en.get('cr','?')}"
                          for en in enemies)
            )
        else:
            self._enc_enemies.setPlainText(str(enemies))
        self._enc_notes.setPlainText(e.get("notes", ""))

    def _collect_encounter_form(self, e: dict):
        e["name"]       = self._enc_name.text().strip() or e.get("name", "Begegnung")
        e["difficulty"] = self._enc_diff.currentText()
        e["xp"]         = self._enc_xp.value()
        e["notes"]      = self._enc_notes.toPlainText()
        lines = self._enc_enemies.toPlainText().strip().splitlines()
        enemies = []
        for line in lines:
            parts = [p.strip() for p in line.split("|")]
            if parts:
                enemies.append({
                    "name": parts[0],
                    "count": int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1,
                    "cr": parts[2].replace("HG", "").strip() if len(parts) > 2 else "?",
                })
        e["enemies"] = enemies

    # ═══════════════════════════════════════════════════════════════════════
    # TAB 5 – Flags & Entscheidungen
    # ═══════════════════════════════════════════════════════════════════════

    def _flags_tab(self) -> QWidget:
        tab = QWidget()
        sp = QSplitter(Qt.Orientation.Vertical)
        tl = QVBoxLayout(tab)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.addWidget(sp)

        # ── Flags ──────────────────────────────────────────────────────────
        flags_w = QWidget()
        flags_w.setStyleSheet(f"background:{COLORS['bg']};")
        fl = QVBoxLayout(flags_w)
        fl.setContentsMargins(12, 12, 12, 8)
        fl.setSpacing(6)

        fl.addWidget(_section("Flags — Spielerentscheidungen und deren Konsequenzen"))

        flag_hint = QLabel(
            "✓ Gesetzt = Spieler haben diese Aktion durchgeführt (GM setzt diesen Haken live).\n"
            "Szenen und Entscheidungen mit Bezug zu diesem Flag werden im Baum farbig markiert."
        )
        flag_hint.setStyleSheet(f"color:{COLORS['muted']};font-size:11px;")
        flag_hint.setWordWrap(True)
        fl.addWidget(flag_hint)

        self._flags_list = QListWidget()
        self._flags_list.setStyleSheet(
            f"QListWidget{{background:{COLORS['surface']};border:1px solid {COLORS['border']};"
            f"border-radius:4px;font-size:12px;}}"
        )
        self._flags_list.currentRowChanged.connect(self._on_flag_select)
        fl.addWidget(self._flags_list, 1)

        flag_btns = QHBoxLayout()
        b_add_flag = _btn("+ Flag", "primary-btn")
        b_del_flag = _btn("− Flag", "secondary-btn")
        b_add_flag.clicked.connect(self._add_flag)
        b_del_flag.clicked.connect(self._del_flag)
        flag_btns.addWidget(b_add_flag)
        flag_btns.addWidget(b_del_flag)
        flag_btns.addStretch()
        fl.addLayout(flag_btns)

        # Flag editor
        fl.addWidget(_sep())
        fl.addWidget(_section("Flag-Details"))
        frow = QHBoxLayout()
        self._flag_name  = _edit("Interner Name (z. B. helped_merchant)")
        self._flag_label = _edit("Anzeigename (z. B. Händler wurde geholfen)")
        self._flag_is_set = QCheckBox("✓ Gesetzt (Spieler haben dies getan)")
        self._flag_is_set.setStyleSheet(
            f"color:{COLORS['success']};font-weight:bold;font-size:12px;"
        )
        self._flag_is_set.stateChanged.connect(self._on_flag_set_changed)
        frow.addWidget(_lbl("Name:", True))
        frow.addWidget(self._flag_name, 1)
        frow.addWidget(_lbl("Label:", True))
        frow.addWidget(self._flag_label, 1)
        frow.addWidget(self._flag_is_set)
        fl.addLayout(frow)

        self._flag_desc = _edit("Beschreibung")
        fl.addWidget(_lbl("Beschreibung:", True))
        fl.addWidget(self._flag_desc)

        # Consequence display
        self._flag_consequence_lbl = QLabel("")
        self._flag_consequence_lbl.setWordWrap(True)
        self._flag_consequence_lbl.setStyleSheet(
            f"color:{COLORS['muted']};font-size:11px;"
            f"background:{COLORS['surface']};border-radius:4px;padding:6px;"
        )
        fl.addWidget(self._flag_consequence_lbl)
        sp.addWidget(flags_w)

        # ── Entscheidungen (global view) ─────────────────────────────────
        dec_w = QWidget()
        dec_w.setStyleSheet(f"background:{COLORS['bg']};")
        dl = QVBoxLayout(dec_w)
        dl.setContentsMargins(12, 8, 12, 12)
        dl.setSpacing(6)
        dl.addWidget(_section("Alle Entscheidungspunkte (Übersicht)"))

        self._dec_overview = QTextEdit()
        self._dec_overview.setReadOnly(True)
        self._dec_overview.setStyleSheet(
            f"background:{COLORS['surface']};color:{COLORS['text']};"
            f"border:1px solid {COLORS['border']};border-radius:4px;"
            f"font-family:monospace;font-size:11px;"
        )
        dl.addWidget(self._dec_overview, 1)

        b_refresh_dec = _btn("Übersicht aktualisieren", "secondary-btn")
        b_refresh_dec.clicked.connect(self._refresh_dec_overview)
        dl.addWidget(b_refresh_dec)
        sp.addWidget(dec_w)
        sp.setSizes([500, 300])

        self._populate_flags_list()
        self._refresh_dec_overview()
        return tab

    # ═══════════════════════════════════════════════════════════════════════
    # Tree management
    # ═══════════════════════════════════════════════════════════════════════

    def _populate_tree(self):
        self._tree.clear()
        for chapter in self._content.get("chapters", []):
            ch_item = QTreeWidgetItem([chapter.get("title", "Kapitel")])
            ch_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "chapter", "id": chapter["id"]})
            ch_item.setFont(0, QFont("", 12, QFont.Weight.Bold))
            ch_item.setForeground(0, QColor(COLORS["accent"]))
            for scene in chapter.get("scenes", []):
                sc_item = QTreeWidgetItem([scene.get("title", "Szene")])
                sc_item.setData(0, Qt.ItemDataRole.UserRole, {
                    "type": "scene", "id": scene["id"], "chapter_id": chapter["id"]
                })
                self._apply_scene_style(sc_item, scene)
                ch_item.addChild(sc_item)
            self._tree.addTopLevelItem(ch_item)
            ch_item.setExpanded(True)

    def _apply_scene_style(self, item: QTreeWidgetItem, scene: dict):
        req = scene.get("required_flags", [])
        if req:
            flags = {f["id"]: f for f in self._content.get("flags", [])}
            unmet = [flags[fid]["label"] for fid in req
                     if fid in flags and not flags[fid].get("is_set", False)]
            if unmet:
                item.setForeground(0, QColor(COLORS["warning"] if "warning" in COLORS else COLORS["gold"]))
                item.setToolTip(0, f"Benötigt (nicht erfüllt): {', '.join(unmet)}")
                return
        item.setForeground(0, QColor(COLORS["text"]))
        item.setToolTip(0, "")

    def _refresh_tree_styles(self):
        for i in range(self._tree.topLevelItemCount()):
            ch_item = self._tree.topLevelItem(i)
            ch_data = ch_item.data(0, Qt.ItemDataRole.UserRole)
            ch = self._find_chapter(ch_data["id"])
            if not ch:
                continue
            for j in range(ch_item.childCount()):
                sc_item = ch_item.child(j)
                sc_data = sc_item.data(0, Qt.ItemDataRole.UserRole)
                scene   = self._find_scene(ch_data["id"], sc_data["id"])
                if scene:
                    self._apply_scene_style(sc_item, scene)

    def _add_chapter(self):
        title, ok = QInputDialog.getText(self, "Kapitel", "Titel:")
        if not ok or not title.strip():
            return
        chapter = {"id": _uid(), "title": title.strip(), "scenes": []}
        self._content.setdefault("chapters", []).append(chapter)
        ch_item = QTreeWidgetItem([title.strip()])
        ch_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "chapter", "id": chapter["id"]})
        ch_item.setFont(0, QFont("", 12, QFont.Weight.Bold))
        ch_item.setForeground(0, QColor(COLORS["accent"]))
        self._tree.addTopLevelItem(ch_item)
        ch_item.setExpanded(True)

    def _add_scene(self):
        cur = self._tree.currentItem()
        if not cur:
            QMessageBox.information(self, "Hinweis", "Bitte zuerst ein Kapitel auswählen.")
            return
        d = cur.data(0, Qt.ItemDataRole.UserRole)
        if d["type"] == "scene":
            cur = cur.parent()
            d   = cur.data(0, Qt.ItemDataRole.UserRole)
        title, ok = QInputDialog.getText(self, "Szene", "Titel:")
        if not ok or not title.strip():
            return
        scene = {
            "id": _uid(), "title": title.strip(), "content": "", "notes": "",
            "linked_npcs": [], "linked_items": [], "linked_encounters": [],
            "skill_checks": [], "decisions": [],
            "required_flags": [], "sets_flags": [],
        }
        chapter = self._find_chapter(d["id"])
        if chapter:
            chapter.setdefault("scenes", []).append(scene)
        sc_item = QTreeWidgetItem([title.strip()])
        sc_item.setData(0, Qt.ItemDataRole.UserRole, {
            "type": "scene", "id": scene["id"], "chapter_id": d["id"]
        })
        cur.addChild(sc_item)
        cur.setExpanded(True)
        self._tree.setCurrentItem(sc_item)

    def _del_tree_item(self):
        cur = self._tree.currentItem()
        if not cur:
            return
        d = cur.data(0, Qt.ItemDataRole.UserRole)
        if QMessageBox.question(
            self, "Löschen", f'"{cur.text(0)}" wirklich löschen?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        ) != QMessageBox.StandardButton.Yes:
            return
        if d["type"] == "chapter":
            self._content["chapters"] = [
                c for c in self._content.get("chapters", []) if c["id"] != d["id"]
            ]
            idx = self._tree.indexOfTopLevelItem(cur)
            self._tree.takeTopLevelItem(idx)
        else:
            ch = self._find_chapter(d["chapter_id"])
            if ch:
                ch["scenes"] = [s for s in ch.get("scenes", []) if s["id"] != d["id"]]
            cur.parent().removeChild(cur)
        self._scene_stack.setCurrentIndex(0)
        self._cur_scene_ids = None

    # ═══════════════════════════════════════════════════════════════════════
    # Scene selection & population
    # ═══════════════════════════════════════════════════════════════════════

    def _on_tree_select(self, cur, prev):
        if prev:
            pd = prev.data(0, Qt.ItemDataRole.UserRole)
            if pd and pd.get("type") == "scene":
                scene = self._find_scene(pd["chapter_id"], pd["id"])
                if scene:
                    self._collect_scene(scene)
                    prev.setText(0, scene["title"])
                    self._apply_scene_style(prev, scene)
        if not cur:
            self._scene_stack.setCurrentIndex(0)
            return
        d = cur.data(0, Qt.ItemDataRole.UserRole)
        if d["type"] == "chapter":
            self._scene_stack.setCurrentIndex(0)
            self._cur_scene_ids = None
            return
        scene = self._find_scene(d["chapter_id"], d["id"])
        if not scene:
            return
        self._cur_scene_ids = (d["chapter_id"], d["id"])
        self._load_scene(scene)
        self._scene_stack.setCurrentIndex(1)

    def _load_scene(self, scene: dict):
        self._se_title.setText(scene.get("title", ""))
        self._se_content.setPlainText(scene.get("content", ""))
        self._se_notes.setPlainText(scene.get("notes", ""))
        self._refresh_link_lists()
        self._populate_scene_links(scene)
        self._populate_scene_decisions(scene)
        self._populate_scene_skill_checks(scene)
        self._populate_scene_flags(scene)
        self._update_flag_banner(scene)

    def _collect_scene(self, scene: dict):
        scene["title"]   = self._se_title.text().strip() or scene.get("title", "Szene")
        scene["content"] = self._se_content.toPlainText()
        scene["notes"]   = self._se_notes.toPlainText()
        # Links
        _, npc_lw = self._link_npcs
        _, item_lw = self._link_items
        _, enc_lw = self._link_encs
        scene["linked_npcs"]       = [npc_lw.item(i).data(Qt.ItemDataRole.UserRole)
                                       for i in range(npc_lw.count())
                                       if npc_lw.item(i).checkState() == Qt.CheckState.Checked]
        scene["linked_items"]      = [item_lw.item(i).data(Qt.ItemDataRole.UserRole)
                                       for i in range(item_lw.count())
                                       if item_lw.item(i).checkState() == Qt.CheckState.Checked]
        scene["linked_encounters"] = [enc_lw.item(i).data(Qt.ItemDataRole.UserRole)
                                       for i in range(enc_lw.count())
                                       if enc_lw.item(i).checkState() == Qt.CheckState.Checked]
        # Required / sets flags
        scene["required_flags"] = [
            self._flag_req_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self._flag_req_list.count())
            if self._flag_req_list.item(i).checkState() == Qt.CheckState.Checked
        ]
        scene["sets_flags"] = [
            self._flag_set_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self._flag_set_list.count())
            if self._flag_set_list.item(i).checkState() == Qt.CheckState.Checked
        ]

    def _refresh_link_lists(self):
        """Repopulate the linkable entity checkboxes from content."""
        _, npc_lw = self._link_npcs
        _, item_lw = self._link_items
        _, enc_lw  = self._link_encs
        npc_lw.clear()
        item_lw.clear()
        enc_lw.clear()
        for e in self._content.get("npcs", []):
            it = QListWidgetItem(e.get("name", "?"))
            it.setData(Qt.ItemDataRole.UserRole, e["id"])
            it.setFlags(it.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            it.setCheckState(Qt.CheckState.Unchecked)
            npc_lw.addItem(it)
        for e in self._content.get("items", []):
            it = QListWidgetItem(e.get("name", "?"))
            it.setData(Qt.ItemDataRole.UserRole, e["id"])
            it.setFlags(it.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            it.setCheckState(Qt.CheckState.Unchecked)
            item_lw.addItem(it)
        for e in self._content.get("encounters", []):
            it = QListWidgetItem(e.get("name", "?"))
            it.setData(Qt.ItemDataRole.UserRole, e["id"])
            it.setFlags(it.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            it.setCheckState(Qt.CheckState.Unchecked)
            enc_lw.addItem(it)

    def _populate_scene_links(self, scene: dict):
        _, npc_lw  = self._link_npcs
        _, item_lw = self._link_items
        _, enc_lw  = self._link_encs
        linked_npcs  = set(scene.get("linked_npcs", []))
        linked_items = set(scene.get("linked_items", []))
        linked_encs  = set(scene.get("linked_encounters", []))
        for i in range(npc_lw.count()):
            it = npc_lw.item(i)
            it.setCheckState(Qt.CheckState.Checked if it.data(Qt.ItemDataRole.UserRole) in linked_npcs
                             else Qt.CheckState.Unchecked)
        for i in range(item_lw.count()):
            it = item_lw.item(i)
            it.setCheckState(Qt.CheckState.Checked if it.data(Qt.ItemDataRole.UserRole) in linked_items
                             else Qt.CheckState.Unchecked)
        for i in range(enc_lw.count()):
            it = enc_lw.item(i)
            it.setCheckState(Qt.CheckState.Checked if it.data(Qt.ItemDataRole.UserRole) in linked_encs
                             else Qt.CheckState.Unchecked)

    def _populate_scene_flags(self, scene: dict):
        flags = self._content.get("flags", [])
        req   = set(scene.get("required_flags", []))
        sets  = set(scene.get("sets_flags", []))
        self._flag_req_list.clear()
        self._flag_set_list.clear()
        for f in flags:
            for lw, checked_set in [(self._flag_req_list, req), (self._flag_set_list, sets)]:
                label = f.get("label") or f.get("name", "?")
                is_set = f.get("is_set", False)
                display = f"{'✓ ' if is_set else '○ '}{label}"
                it = QListWidgetItem(display)
                it.setData(Qt.ItemDataRole.UserRole, f["id"])
                it.setFlags(it.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                it.setCheckState(Qt.CheckState.Checked if f["id"] in checked_set
                                 else Qt.CheckState.Unchecked)
                color = COLORS["success"] if is_set else COLORS["muted"]
                it.setForeground(QColor(color))
                lw.addItem(it)

    def _update_flag_banner(self, scene: dict):
        req = scene.get("required_flags", [])
        sets = scene.get("sets_flags", [])
        if not req and not sets:
            self._flag_banner.setVisible(False)
            return
        flags_map = {f["id"]: f for f in self._content.get("flags", [])}
        parts = []
        for fid in req:
            f = flags_map.get(fid)
            if f:
                status = "✓" if f.get("is_set") else "✗"
                color  = "green" if f.get("is_set") else "red"
                parts.append(f'<span style="color:{color};">{status} Benötigt: {f.get("label", fid)}</span>')
        for fid in sets:
            f = flags_map.get(fid)
            if f:
                parts.append(f'<span style="color:{COLORS["gold"]};">→ Setzt: {f.get("label", fid)}</span>')
        if parts:
            self._flag_banner.setText("  |  ".join(parts))
            self._flag_banner.setVisible(True)
        else:
            self._flag_banner.setVisible(False)

    # ── Decisions ─────────────────────────────────────────────────────────

    def _populate_scene_decisions(self, scene: dict):
        self._dec_list.clear()
        for d in scene.get("decisions", []):
            it = QListWidgetItem(d.get("description", "?"))
            it.setData(Qt.ItemDataRole.UserRole, d)
            self._dec_list.addItem(it)
        self._clear_dec_form()

    def _on_dec_select(self, row: int):
        if row < 0:
            self._clear_dec_form()
            return
        item = self._dec_list.item(row)
        dec  = item.data(Qt.ItemDataRole.UserRole)
        self._dec_desc.setText(dec.get("description", ""))
        # Clear and repopulate option rows
        while self._dec_options_layout.count():
            w = self._dec_options_layout.takeAt(0)
            if w.widget():
                w.widget().deleteLater()
        for opt in dec.get("options", []):
            self._add_option_row(opt)

    def _clear_dec_form(self):
        self._dec_desc.clear()
        while self._dec_options_layout.count():
            w = self._dec_options_layout.takeAt(0)
            if w.widget():
                w.widget().deleteLater()

    def _add_decision(self):
        dec = {"id": _uid(), "description": "Neue Entscheidung", "options": []}
        scene = self._cur_scene()
        if scene:
            scene.setdefault("decisions", []).append(dec)
            it = QListWidgetItem(dec["description"])
            it.setData(Qt.ItemDataRole.UserRole, dec)
            self._dec_list.addItem(it)
            self._dec_list.setCurrentRow(self._dec_list.count() - 1)

    def _del_decision(self):
        row = self._dec_list.currentRow()
        if row < 0:
            return
        dec  = self._dec_list.item(row).data(Qt.ItemDataRole.UserRole)
        scene = self._cur_scene()
        if scene:
            scene["decisions"] = [d for d in scene.get("decisions", []) if d["id"] != dec["id"]]
        self._dec_list.takeItem(row)
        self._clear_dec_form()

    def _add_option_row(self, opt: dict | None = None):
        row_w = QWidget()
        row_w.setStyleSheet(
            f"background:{COLORS['surface']};border-radius:4px;"
        )
        rl = QHBoxLayout(row_w)
        rl.setContentsMargins(6, 4, 6, 4)
        rl.setSpacing(4)

        e_text = _edit("Option-Text (was wählen Spieler?)")
        e_cons = _edit("Konsequenz")
        flags  = self._content.get("flags", [])
        flag_combo = _combo(["— kein Flag —"] + [f.get("label", f["name"]) for f in flags])

        b_set = _btn("✓ Setzen", "primary-btn", 80)

        if opt:
            e_text.setText(opt.get("text", ""))
            e_cons.setText(opt.get("consequence", ""))
            fid = opt.get("sets_flag", "")
            for i, f in enumerate(flags):
                if f["id"] == fid:
                    flag_combo.setCurrentIndex(i + 1)
                    break

        def _set_flag():
            fi = flag_combo.currentIndex() - 1
            if fi < 0:
                return
            flags[fi]["is_set"] = True
            self._populate_flags_list()
            self._refresh_tree_styles()
            QMessageBox.information(self, "Flag gesetzt",
                                    f'Flag "{flags[fi].get("label", flags[fi]["name"])}" wurde gesetzt!')

        b_set.clicked.connect(_set_flag)
        b_del = _btn("×", "secondary-btn", 28)
        b_del.clicked.connect(lambda: (rl.parentWidget().deleteLater()))

        rl.addWidget(e_text, 2)
        rl.addWidget(e_cons, 2)
        rl.addWidget(_lbl("→ Flag:", True))
        rl.addWidget(flag_combo, 1)
        rl.addWidget(b_set)
        rl.addWidget(b_del)
        self._dec_options_layout.addWidget(row_w)

    def _save_dec_form(self):
        row = self._dec_list.currentRow()
        if row < 0:
            return
        item = self._dec_list.item(row)
        dec  = item.data(Qt.ItemDataRole.UserRole)
        dec["description"] = self._dec_desc.text().strip() or dec.get("description", "Entscheidung")
        item.setText(dec["description"])
        options = []
        flags = self._content.get("flags", [])
        for i in range(self._dec_options_layout.count()):
            w = self._dec_options_layout.itemAt(i).widget()
            if not w:
                continue
            children = w.findChildren(QLineEdit)
            combo    = w.findChild(QComboBox)
            if len(children) >= 2:
                fi = (combo.currentIndex() - 1) if combo else -1
                options.append({
                    "text": children[0].text(),
                    "consequence": children[1].text(),
                    "sets_flag": flags[fi]["id"] if fi >= 0 else "",
                })
        dec["options"] = options
        item.setData(Qt.ItemDataRole.UserRole, dec)

    # ── Skill Checks ──────────────────────────────────────────────────────

    def _populate_scene_skill_checks(self, scene: dict):
        self._sc_list.clear()
        for sc in scene.get("skill_checks", []):
            it = QListWidgetItem(f"{sc.get('skill','?')} SG {sc.get('dc',10)}")
            it.setData(Qt.ItemDataRole.UserRole, sc)
            self._sc_list.addItem(it)

    def _on_sc_select(self, row: int):
        if row < 0:
            return
        sc = self._sc_list.item(row).data(Qt.ItemDataRole.UserRole)
        idx = SKILLS.index(sc.get("skill", SKILLS[0])) if sc.get("skill") in SKILLS else 0
        self._sc_skill.setCurrentIndex(idx)
        self._sc_dc.setValue(sc.get("dc", 12))
        self._sc_success.setPlainText(sc.get("success", ""))
        self._sc_failure.setPlainText(sc.get("failure", ""))

    def _add_skill_check(self):
        sc = {"id": _uid(), "skill": SKILLS[0], "dc": 12, "success": "", "failure": ""}
        scene = self._cur_scene()
        if scene:
            scene.setdefault("skill_checks", []).append(sc)
            it = QListWidgetItem(f"{sc['skill']} SG {sc['dc']}")
            it.setData(Qt.ItemDataRole.UserRole, sc)
            self._sc_list.addItem(it)
            self._sc_list.setCurrentRow(self._sc_list.count() - 1)

    def _del_skill_check(self):
        row = self._sc_list.currentRow()
        if row < 0:
            return
        sc = self._sc_list.item(row).data(Qt.ItemDataRole.UserRole)
        scene = self._cur_scene()
        if scene:
            scene["skill_checks"] = [
                s for s in scene.get("skill_checks", []) if s.get("id") != sc.get("id")
            ]
        self._sc_list.takeItem(row)

    def _save_sc_form(self):
        row = self._sc_list.currentRow()
        if row < 0:
            return
        item = self._sc_list.item(row)
        sc   = item.data(Qt.ItemDataRole.UserRole)
        sc["skill"]   = self._sc_skill.currentText()
        sc["dc"]      = self._sc_dc.value()
        sc["success"] = self._sc_success.toPlainText()
        sc["failure"] = self._sc_failure.toPlainText()
        item.setText(f"{sc['skill']} SG {sc['dc']}")
        item.setData(Qt.ItemDataRole.UserRole, sc)

    # ── Flags list ────────────────────────────────────────────────────────

    def _populate_flags_list(self):
        self._flags_list.clear()
        for f in self._content.get("flags", []):
            label  = f.get("label") or f.get("name", "?")
            is_set = f.get("is_set", False)
            display = f"{'✓' if is_set else '○'}  {label}"
            it = QListWidgetItem(display)
            it.setData(Qt.ItemDataRole.UserRole, f["id"])
            it.setForeground(QColor(COLORS["success"] if is_set else COLORS["muted"]))
            self._flags_list.addItem(it)

    def _on_flag_select(self, row: int):
        if row < 0:
            self._flag_consequence_lbl.setText("")
            return
        fid = self._flags_list.item(row).data(Qt.ItemDataRole.UserRole)
        f   = self._find_entity("flags", fid)
        if not f:
            return
        self._flag_name.setText(f.get("name", ""))
        self._flag_label.setText(f.get("label", ""))
        self._flag_desc.setText(f.get("description", ""))
        self._flag_is_set.blockSignals(True)
        self._flag_is_set.setChecked(f.get("is_set", False))
        self._flag_is_set.blockSignals(False)
        # Consequence display
        req_scenes  = []
        sets_scenes = []
        for ch in self._content.get("chapters", []):
            for sc in ch.get("scenes", []):
                if fid in sc.get("required_flags", []):
                    req_scenes.append(f"  • {ch['title']} → {sc['title']}")
                if fid in sc.get("sets_flags", []):
                    sets_scenes.append(f"  • {ch['title']} → {sc['title']}")
        lines = []
        if req_scenes:
            lines.append("Wird benötigt von:")
            lines.extend(req_scenes)
        if sets_scenes:
            lines.append("Wird gesetzt von:")
            lines.extend(sets_scenes)
        self._flag_consequence_lbl.setText("\n".join(lines) if lines else "Keine Szene verweist auf diesen Flag.")

    def _on_flag_set_changed(self, state: int):
        row = self._flags_list.currentRow()
        if row < 0:
            return
        fid = self._flags_list.item(row).data(Qt.ItemDataRole.UserRole)
        f   = self._find_entity("flags", fid)
        if f:
            f["is_set"] = (state == Qt.CheckState.Checked.value)
            self._populate_flags_list()
            self._flags_list.setCurrentRow(row)
            self._refresh_tree_styles()
            if self._cur_scene_ids:
                ch_id, sc_id = self._cur_scene_ids
                scene = self._find_scene(ch_id, sc_id)
                if scene:
                    self._update_flag_banner(scene)
                    self._populate_scene_flags(scene)

    def _add_flag(self):
        name, ok = QInputDialog.getText(self, "Flag", "Interner Name (z. B. helped_merchant):")
        if not ok or not name.strip():
            return
        label, ok2 = QInputDialog.getText(self, "Flag", "Anzeigename (z. B. Händler wurde geholfen):")
        if not ok2:
            label = name.strip()
        f = {"id": _uid(), "name": name.strip(), "label": label.strip(), "description": "", "is_set": False}
        self._content.setdefault("flags", []).append(f)
        self._populate_flags_list()
        self._flags_list.setCurrentRow(self._flags_list.count() - 1)

    def _del_flag(self):
        row = self._flags_list.currentRow()
        if row < 0:
            return
        fid = self._flags_list.item(row).data(Qt.ItemDataRole.UserRole)
        self._content["flags"] = [
            f for f in self._content.get("flags", []) if f["id"] != fid
        ]
        self._populate_flags_list()

    def _save_flag_form(self):
        row = self._flags_list.currentRow()
        if row < 0:
            return
        fid = self._flags_list.item(row).data(Qt.ItemDataRole.UserRole)
        f   = self._find_entity("flags", fid)
        if f:
            f["name"]        = self._flag_name.text().strip() or f.get("name", "flag")
            f["label"]       = self._flag_label.text().strip() or f["name"]
            f["description"] = self._flag_desc.text().strip()
            f["is_set"]      = self._flag_is_set.isChecked()

    # ── Decision overview ─────────────────────────────────────────────────

    def _refresh_dec_overview(self):
        lines = []
        for ch in self._content.get("chapters", []):
            ch_has = False
            for sc in ch.get("scenes", []):
                for dec in sc.get("decisions", []):
                    if not ch_has:
                        lines.append(f"=== {ch.get('title','?')} ===")
                        ch_has = True
                    lines.append(f"  [{sc.get('title','?')}] {dec.get('description','?')}")
                    for opt in dec.get("options", []):
                        fid = opt.get("sets_flag", "")
                        flag_label = ""
                        if fid:
                            f = self._find_entity("flags", fid)
                            flag_label = f" → setzt [{f.get('label', fid)}]" if f else ""
                        lines.append(f"    ▸ {opt.get('text','?')} : {opt.get('consequence','')}{flag_label}")
        self._dec_overview.setPlainText("\n".join(lines) if lines else "(Noch keine Entscheidungen definiert.)")

    # ═══════════════════════════════════════════════════════════════════════
    # Save
    # ═══════════════════════════════════════════════════════════════════════

    def _save(self):
        # Flush current scene/entity forms
        if self._cur_scene_ids:
            ch_id, sc_id = self._cur_scene_ids
            scene = self._find_scene(ch_id, sc_id)
            if scene:
                self._collect_scene(scene)
        if self._cur_npc_id:
            npc = self._find_entity("npcs", self._cur_npc_id)
            if npc:
                self._collect_npc_form(npc)
        if self._cur_item_id:
            item = self._find_entity("items", self._cur_item_id)
            if item:
                self._collect_item_form(item)
        if self._cur_enc_id:
            enc = self._find_entity("encounters", self._cur_enc_id)
            if enc:
                self._collect_encounter_form(enc)
        self._save_dec_form()
        self._save_sc_form()
        self._save_flag_form()

        try:
            r = requests.put(
                f"{self._base_url}/api/campaigns/{self._campaign['id']}",
                json={
                    "name":    self._name_edit.text().strip() or self._campaign["name"],
                    "content": self._content,
                },
                headers={"Authorization": f"Bearer {self._token}"},
                timeout=5,
            )
            if r.ok:
                QMessageBox.information(self, "Gespeichert", "Kampagne erfolgreich gespeichert.")
                self._refresh_dec_overview()
            else:
                QMessageBox.warning(self, "Fehler", r.json().get("error", "Unbekannt"))
        except Exception as e:
            QMessageBox.warning(self, "Netzwerkfehler", str(e))

    # ═══════════════════════════════════════════════════════════════════════
    # Helpers
    # ═══════════════════════════════════════════════════════════════════════

    def _find_chapter(self, ch_id: str) -> dict | None:
        return next(
            (c for c in self._content.get("chapters", []) if c["id"] == ch_id), None
        )

    def _find_scene(self, ch_id: str, sc_id: str) -> dict | None:
        ch = self._find_chapter(ch_id)
        if not ch:
            return None
        return next((s for s in ch.get("scenes", []) if s["id"] == sc_id), None)

    def _find_entity(self, key: str, eid: str) -> dict | None:
        return next(
            (e for e in self._content.get(key, []) if e.get("id") == eid), None
        )

    def _cur_scene(self) -> dict | None:
        if not self._cur_scene_ids:
            return None
        return self._find_scene(*self._cur_scene_ids)
