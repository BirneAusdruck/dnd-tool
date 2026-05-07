"""
Initiative Tracker panel – GM tool for combat order management.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QSpinBox, QListWidget, QListWidgetItem, QFrame,
    QMenu, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont

from src.client.gui.theme import COLORS


class _CombatantWidget(QWidget):
    """Row widget inside the initiative list."""

    hp_changed = Signal(str, int)  # name, new_hp
    removed = Signal(str)

    def __init__(self, name: str, initiative: int, hp: int, hp_max: int, is_current: bool = False):
        super().__init__()
        self.combatant_name = name
        self.hp = hp
        self.hp_max = hp_max

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(6)

        # Initiative badge
        init_lbl = QLabel(str(initiative))
        init_lbl.setFixedWidth(28)
        init_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge_color = COLORS["accent"] if is_current else COLORS["overlay"]
        init_lbl.setStyleSheet(
            f"background:{badge_color};color:white;border-radius:4px;font-weight:bold;font-size:11px;"
        )

        # Name
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(
            f"color:{'white' if is_current else COLORS['text']};font-weight:{'bold' if is_current else 'normal'};font-size:12px;"
        )
        name_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # HP display + edit
        self.hp_spin = QSpinBox()
        self.hp_spin.setRange(0, 9999)
        self.hp_spin.setValue(hp)
        self.hp_spin.setFixedWidth(58)
        self.hp_spin.setStyleSheet(
            f"color:{self._hp_color()};background:{COLORS['bg']};border:1px solid {COLORS['border']};border-radius:3px;font-size:11px;"
        )
        self.hp_spin.valueChanged.connect(lambda v: self._on_hp_change(v))

        hp_max_lbl = QLabel(f"/{hp_max}")
        hp_max_lbl.setStyleSheet(f"color:{COLORS['muted']};font-size:11px;")

        layout.addWidget(init_lbl)
        layout.addWidget(name_lbl, 1)
        layout.addWidget(self.hp_spin)
        layout.addWidget(hp_max_lbl)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._context_menu)

    def _hp_color(self) -> str:
        ratio = self.hp / max(1, self.hp_max)
        if ratio > 0.5:
            return COLORS["success"]
        elif ratio > 0.25:
            return COLORS["warning"]
        return COLORS["error"]

    def _on_hp_change(self, value: int) -> None:
        self.hp = value
        self.hp_spin.setStyleSheet(
            f"color:{self._hp_color()};background:{COLORS['bg']};border:1px solid {COLORS['border']};border-radius:3px;font-size:11px;"
        )
        self.hp_changed.emit(self.combatant_name, value)

    def _context_menu(self, pos):
        menu = QMenu(self)
        act_remove = menu.addAction("Entfernen")
        act = menu.exec(self.mapToGlobal(pos))
        if act == act_remove:
            self.removed.emit(self.combatant_name)


class InitiativePanel(QWidget):
    """Right-side initiative tracker panel."""

    combatant_hp_changed = Signal(str, int)   # name, hp

    def __init__(self, parent=None):
        super().__init__(parent)
        self._combatants: list[dict] = []   # [{name, initiative, hp, hp_max}]
        self._current_index = -1
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Header
        header = QLabel("⚔ Initiative")
        header.setStyleSheet(f"color:{COLORS['accent']};font-size:15px;font-weight:bold;")
        layout.addWidget(header)

        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep)

        # Add combatant form
        add_grp = QWidget()
        add_layout = QVBoxLayout(add_grp)
        add_layout.setContentsMargins(0, 0, 0, 0)
        add_layout.setSpacing(4)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Name (Charakter / Monster)")
        add_layout.addWidget(self.name_edit)

        row = QHBoxLayout()
        self.init_spin = QSpinBox()
        self.init_spin.setRange(-5, 40)
        self.init_spin.setValue(10)
        self.init_spin.setPrefix("Init: ")
        self.init_spin.setFixedWidth(90)

        self.hp_spin = QSpinBox()
        self.hp_spin.setRange(1, 9999)
        self.hp_spin.setValue(10)
        self.hp_spin.setPrefix("HP: ")
        self.hp_spin.setFixedWidth(90)

        btn_add = QPushButton("+")
        btn_add.setObjectName("primary-btn")
        btn_add.setFixedWidth(32)
        btn_add.clicked.connect(self._add_combatant)
        self.name_edit.returnPressed.connect(self._add_combatant)

        row.addWidget(self.init_spin)
        row.addWidget(self.hp_spin)
        row.addWidget(btn_add)
        add_layout.addLayout(row)
        layout.addWidget(add_grp)

        # Combatant list
        self.list_widget = QListWidget()
        self.list_widget.setSpacing(2)
        self.list_widget.setStyleSheet(
            f"QListWidget{{background:{COLORS['bg']};border:1px solid {COLORS['border']};border-radius:6px;}}"
            f"QListWidget::item{{border-radius:4px;padding:0;}}"
            f"QListWidget::item:selected{{background:{COLORS['surface']};}}"
        )
        layout.addWidget(self.list_widget, 1)

        # Round info
        self.round_lbl = QLabel("Runde 1")
        self.round_lbl.setStyleSheet(f"color:{COLORS['gold']};font-weight:bold;text-align:center;")
        self.round_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.round_lbl)
        self._round = 1

        # Navigation buttons
        nav = QHBoxLayout()
        self.btn_prev = QPushButton("◀")
        self.btn_prev.setObjectName("secondary-btn")
        self.btn_prev.clicked.connect(self._prev_turn)
        self.btn_next = QPushButton("▶  Nächster")
        self.btn_next.setObjectName("primary-btn")
        self.btn_next.clicked.connect(self._next_turn)
        nav.addWidget(self.btn_prev)
        nav.addWidget(self.btn_next, 1)
        layout.addLayout(nav)

        # Action buttons
        actions = QHBoxLayout()
        btn_sort = QPushButton("Sortieren")
        btn_sort.setObjectName("secondary-btn")
        btn_sort.clicked.connect(self._sort_initiative)
        btn_clear = QPushButton("Leeren")
        btn_clear.setObjectName("secondary-btn")
        btn_clear.clicked.connect(self._clear)
        actions.addWidget(btn_sort)
        actions.addWidget(btn_clear)
        layout.addLayout(actions)

    # ── Combatant management ──────────────────────────────────────────────

    def _add_combatant(self):
        name = self.name_edit.text().strip()
        if not name:
            return
        entry = {
            "name": name,
            "initiative": self.init_spin.value(),
            "hp": self.hp_spin.value(),
            "hp_max": self.hp_spin.value(),
        }
        self._combatants.append(entry)
        self.name_edit.clear()
        self._refresh_list()

    def add_from_character(self, name: str, initiative: int, hp_max: int) -> None:
        self._combatants.append({
            "name": name,
            "initiative": initiative,
            "hp": hp_max,
            "hp_max": hp_max,
        })
        self._refresh_list()

    def _sort_initiative(self):
        self._combatants.sort(key=lambda c: c["initiative"], reverse=True)
        self._current_index = 0 if self._combatants else -1
        self._refresh_list()

    def _clear(self):
        self._combatants.clear()
        self._current_index = -1
        self._round = 1
        self.round_lbl.setText("Runde 1")
        self._refresh_list()

    def _next_turn(self):
        if not self._combatants:
            return
        self._current_index = (self._current_index + 1) % len(self._combatants)
        if self._current_index == 0:
            self._round += 1
            self.round_lbl.setText(f"Runde {self._round}")
        self._refresh_list()

    def _prev_turn(self):
        if not self._combatants:
            return
        self._current_index = (self._current_index - 1) % len(self._combatants)
        self._refresh_list()

    def _remove_by_name(self, name: str):
        self._combatants = [c for c in self._combatants if c["name"] != name]
        if self._current_index >= len(self._combatants):
            self._current_index = max(0, len(self._combatants) - 1)
        self._refresh_list()

    def _on_hp_changed(self, name: str, hp: int):
        for c in self._combatants:
            if c["name"] == name:
                c["hp"] = hp
                break
        self.combatant_hp_changed.emit(name, hp)

    # ── List rendering ────────────────────────────────────────────────────

    def _refresh_list(self):
        self.list_widget.clear()
        for i, c in enumerate(self._combatants):
            is_current = (i == self._current_index)
            widget = _CombatantWidget(c["name"], c["initiative"], c["hp"], c["hp_max"], is_current)
            widget.hp_changed.connect(self._on_hp_changed)
            widget.removed.connect(self._remove_by_name)

            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())
            if is_current:
                item.setBackground(QColor(COLORS["surface"]))
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)

    # ── State serialization ───────────────────────────────────────────────

    def get_state(self) -> dict:
        return {
            "combatants": self._combatants,
            "current_index": self._current_index,
            "round": self._round,
        }

    def set_state(self, state: dict) -> None:
        self._combatants = state.get("combatants", [])
        self._current_index = state.get("current_index", -1)
        self._round = state.get("round", 1)
        self.round_lbl.setText(f"Runde {self._round}")
        self._refresh_list()
