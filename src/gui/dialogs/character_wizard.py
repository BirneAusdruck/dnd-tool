"""
7-step character creation wizard for DnD 5e / 5.5e.

Steps:
  0 – Edition & Name
  1 – Race / Species
  2 – Class
  3 – Ability Scores
  4 – Background
  5 – Skills
  6 – Spells (spellcasters only) / Finish
"""

from __future__ import annotations
import random

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QPushButton, QLabel, QLineEdit, QComboBox, QListWidget,
    QListWidgetItem, QGroupBox, QGridLayout, QScrollArea, QFrame,
    QButtonGroup, QRadioButton, QSpinBox, QTextEdit, QCheckBox,
    QSizePolicy, QWidget,
)
from PySide6.QtCore import Qt

import requests

from src.gui.theme import COLORS
from src.game import srd_loader as srd
from src.game.character_builder import (
    build_character_data, STANDARD_ARRAY, POINT_BUY_COSTS,
    POINT_BUY_BUDGET, modifier,
)
from src.game.level_manager import apply_level_up, get_level_up_info


# ── Helper widgets ─────────────────────────────────────────────────────────

def _section(title: str) -> QLabel:
    lbl = QLabel(title)
    lbl.setStyleSheet(f"font-size:15px;font-weight:bold;color:{COLORS['accent']};margin-bottom:4px;")
    return lbl


def _hint(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    lbl.setStyleSheet(f"color:{COLORS['muted']};font-size:12px;")
    return lbl


def _scroll_wrap(inner: QWidget) -> QScrollArea:
    sa = QScrollArea()
    sa.setWidgetResizable(True)
    sa.setFrameShape(QFrame.Shape.NoFrame)
    sa.setWidget(inner)
    return sa


# ── Step pages ─────────────────────────────────────────────────────────────

class _Step0_BasicInfo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.addWidget(_section("Schritt 1 – Edition & Grunddaten"))

        # Edition
        ed_grp = QGroupBox("Regelwerk-Edition")
        ed_inner = QVBoxLayout(ed_grp)

        basic_grp = QGroupBox("Basis Regelwerk")
        basic_inner = QVBoxLayout(basic_grp)
        # rule5ebasic_grp = QGroupBox()
        # rule5ebasic_inner = QVBoxLayout(rule5ebasic_grp)
        # rule55ebasic_grp = QGroupBox()
        # rule55ebasic_inner = QVBoxLayout(rule55ebasic_grp)
        phb_grp = QGroupBox("Offizielles Spielerhandbuch Regelwerk")
        phb_inner = QVBoxLayout(phb_grp)
        rule5e_grp = QGroupBox()
        rule5e_inner = QVBoxLayout(rule5e_grp)
        rule55e_grp = QGroupBox()
        rule55e_inner = QVBoxLayout(rule55e_grp)
        srd_grp = QGroupBox("System Reference Document Regelwerk")
        srd_inner = QVBoxLayout(srd_grp)
        rule51srd_grp = QGroupBox()
        rule51srd_inner = QVBoxLayout(rule51srd_grp)
        rule52srd_grp = QGroupBox()
        rule52srd_inner = QVBoxLayout(rule52srd_grp)

        self.rb_5e_basic = QRadioButton("D&D 5e (2014 Basic) (Not Implemented Yet!)")
        self.rb_55e_basic = QRadioButton("D&D 5.5e (2024 Basic) (Not Implemented Yet!)")
        self.rb_5e = QRadioButton("D&D 5e (2014 PHB) (Not Implemented Yet!)")
        self.cb_5e_advanced = QCheckBox("D&D 5e Advanced Rule Set (Not Implemented Yet!)")
        self.rb_55e = QRadioButton("D&D 5.5e (2024 PHB) (Not Implemented Yet!)")
        self.cb_55e_advanced = QCheckBox("D&D 5.5e Advanced Rule Set (Not Implemented Yet!)")
        self.rb_51_srd = QRadioButton("SRD 5.1")
        self.cb_51_custom = QCheckBox("SRD 5.1 Custom Content (Not Implemented Yet!)")
        self.rb_52_srd = QRadioButton("SRD 5.2")
        self.cb_52_custom = QCheckBox("SRD 5.2 Custom Content (Not Implemented Yet!)")

        # self.rb_5e_basic.setChecked(True)
        self.rb_51_srd.setChecked(True)

        self.cb_5e_advanced.setEnabled(False)
        self.cb_55e_advanced.setEnabled(False)
        # self.cb_51_custom.setEnabled(False)
        self.cb_52_custom.setEnabled(False)

        _cb_style = (
            f"QCheckBox {{ padding-left: 16px; color: {COLORS['subtext']}; }}"
            f"QCheckBox:disabled {{ color: {COLORS['muted']}; }}"
        )
        self.cb_5e_advanced.setStyleSheet(_cb_style)
        self.cb_55e_advanced.setStyleSheet(_cb_style)
        self.cb_51_custom.setStyleSheet(_cb_style)
        self.cb_52_custom.setStyleSheet(_cb_style)

        basic_inner.addWidget(self.rb_5e_basic)
        basic_inner.addWidget(self.rb_55e_basic)
        # rule5ebasic_inner.addWidget(self.rb_5e_basic)
        # rule55ebasic_inner.addWidget(self.rb_55e_basic)
        phb_inner.addWidget(rule5e_grp)
        phb_inner.addWidget(rule55e_grp)
        rule5e_inner.addWidget(self.rb_5e)
        rule5e_inner.addWidget(self.cb_5e_advanced)
        rule55e_inner.addWidget(self.rb_55e)
        rule55e_inner.addWidget(self.cb_55e_advanced)
        srd_inner.addWidget(rule51srd_grp)
        srd_inner.addWidget(rule52srd_grp)
        rule51srd_inner.addWidget(self.rb_51_srd)
        rule51srd_inner.addWidget(self.cb_51_custom)
        rule52srd_inner.addWidget(self.rb_52_srd)
        rule52srd_inner.addWidget(self.cb_52_custom)

        ed_container = QWidget()
        ed_container_layout = QVBoxLayout(ed_container)
        ed_container_layout.setContentsMargins(0, 0, 0, 0)
        ed_container_layout.addWidget(basic_grp)
        ed_container_layout.addWidget(phb_grp)
        ed_container_layout.addWidget(srd_grp)
        ed_container_layout.addStretch()

        ed_scroll = QScrollArea()
        ed_scroll.setWidgetResizable(True)
        ed_scroll.setFrameShape(QFrame.Shape.NoFrame)
        ed_scroll.setWidget(ed_container)
        ed_scroll.setMaximumHeight(280)

        ed_inner.addWidget(ed_scroll)

        layout.addWidget(ed_grp)

        self._ed_rbs : list[QRadioButton] = []
        self._ed_rbs.append(self.rb_5e_basic)
        self._ed_rbs.append(self.rb_55e_basic)
        self._ed_rbs.append(self.rb_5e)
        self._ed_rbs.append(self.rb_55e)
        self._ed_rbs.append(self.rb_51_srd)
        self._ed_rbs.append(self.rb_52_srd)
        self._connect_edition_radio_buttons()

        # Name
        name_grp = QGroupBox("Charakter-Name")
        name_inner = QVBoxLayout(name_grp)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("z.B. Thoradin Eisenschild")
        name_inner.addWidget(self.name_edit)
        layout.addWidget(name_grp)

        # Alignment
        align_grp = QGroupBox("Gesinnung")
        align_inner = QVBoxLayout(align_grp)
        self.align_combo = QComboBox()
        for a in srd.ALIGNMENTS:
            self.align_combo.addItem(a)
        align_inner.addWidget(self.align_combo)
        layout.addWidget(align_grp)

        # # Starting level
        # level_grp = QGroupBox("Startlevel")
        # level_inner = QVBoxLayout(level_grp)
        # level_row = QHBoxLayout()
        # self.starting_level_spin = QSpinBox()
        # self.starting_level_spin.setRange(1, 20)
        # self.starting_level_spin.setValue(1)
        # self.starting_level_spin.setFixedWidth(70)
        # level_row.addWidget(QLabel("Level:"))
        # level_row.addWidget(self.starting_level_spin)
        # level_row.addStretch()
        # level_inner.addLayout(level_row)
        # self._level_hint = QLabel("")
        # self._level_hint.setStyleSheet(f"color:{COLORS['muted']};font-size:12px;")
        # self._level_hint.setWordWrap(True)
        # level_inner.addWidget(self._level_hint)
        # self.starting_level_spin.valueChanged.connect(self._on_level_changed)
        # layout.addWidget(level_grp)

        layout.addStretch()

    def edition(self) -> str:
        if self.rb_5e_basic.isChecked():   return "5e_basic"
        elif self.rb_55e_basic.isChecked():  return "5.5e_basic"
        elif self.rb_5e.isChecked() and self.cb_5e_advanced.isChecked(): return "5e_adv"
        elif self.rb_5e.isChecked():         return "5e_phb"
        elif self.rb_55e.isChecked() and self.cb_55e_advanced.isChecked(): return "5.5e_adv"
        elif self.rb_55e.isChecked():        return "5.5e_phb"
        elif self.rb_51_srd.isChecked() and self.cb_51_custom.isChecked(): return "5.1_srd_custom"
        elif self.rb_51_srd.isChecked():     return "5.1_srd"
        elif self.rb_52_srd.isChecked() and self.cb_52_custom.isChecked(): return "5.2_srd_custom"
        elif self.rb_52_srd.isChecked():     return "5.2_srd"
        return "5.1_srd"

    # def _on_level_changed(self, value: int) -> None:
    #     if value > 1:
    #         self._level_hint.setText(
    #             f"Level {value}: Du wirst nach der Erstellung {value - 1}× durch den "
    #             f"Level-Up-Dialog geführt (HP, ASI-Auswahl etc.)."
    #         )
    #     else:
    #         self._level_hint.setText("")

    def validate(self) -> str | None:
        if not self.name_edit.text().strip():
            return "Bitte einen Charakter-Namen eingeben."
        return None

    # def starting_level(self) -> int:
    #     return self.starting_level_spin.value()
    
    def _connect_edition_radio_buttons(self) -> None:
        group = QButtonGroup(self)
        for rb in self._ed_rbs:
            group.addButton(rb)   # Qt verwaltet mutual exclusion automatisch

        self.rb_5e.toggled.connect(self.cb_5e_advanced.setEnabled)
        self.rb_55e.toggled.connect(self.cb_55e_advanced.setEnabled)
        self.rb_51_srd.toggled.connect(self.cb_51_custom.setEnabled)
        self.rb_52_srd.toggled.connect(self.cb_52_custom.setEnabled)
        

class _Step1_Race(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._races = srd.get_races()
        self._build()

    def _build(self):
        outer = QWidget()
        layout = QVBoxLayout(outer)
        layout.setSpacing(12)
        layout.addWidget(_section("Schritt 2 – Rasse / Spezies"))
        layout.addWidget(_hint("Wähle deine Rasse und ggf. Unterrasse aus."))

        row = QHBoxLayout()

        # Left: race list
        left = QVBoxLayout()
        left.addWidget(QLabel("Rasse:"))
        self.race_list = QListWidget()
        self.race_list.setMaximumWidth(200)
        for r in self._races:
            item = QListWidgetItem(r["name"])
            item.setData(Qt.ItemDataRole.UserRole, r["index"])
            self.race_list.addItem(item)
        self.race_list.currentItemChanged.connect(self._on_race_changed)
        left.addWidget(self.race_list)
        row.addLayout(left)

        # Middle: subrace list
        mid = QVBoxLayout()
        mid.addWidget(QLabel("Unterrasse:"))
        self.subrace_list = QListWidget()
        self.subrace_list.setMaximumWidth(180)
        self.subrace_list.currentItemChanged.connect(self._on_subrace_changed)
        mid.addWidget(self.subrace_list)
        row.addLayout(mid)

        # Right: detail panel
        right = QVBoxLayout()
        right.addWidget(QLabel("Details:"))
        self.detail_area = QTextEdit()
        self.detail_area.setReadOnly(True)
        self.detail_area.setMinimumWidth(300)
        right.addWidget(self.detail_area)
        row.addLayout(right, 1)

        layout.addLayout(row)
        layout.addStretch()

        # Half-elf score choices
        self.half_elf_group = QGroupBox("Halbelf: 2 Attribute wählen (+1 je)")
        he_inner = QVBoxLayout(self.half_elf_group)
        self.he_combos = []
        for i in range(2):
            cb = QComboBox()
            for ab in srd.ABILITIES:
                if ab != "CHA":
                    cb.addItem(ab)
            if i == 1:
                cb.setCurrentIndex(1)
            he_inner.addWidget(cb)
            self.he_combos.append(cb)
        self.half_elf_group.setVisible(False)
        layout.addWidget(self.half_elf_group)

        # Dragonborn ancestry
        self.dragonborn_group = QGroupBox("Drakonische Abstammung wählen")
        db_inner = QVBoxLayout(self.dragonborn_group)
        self.dragonborn_combo = QComboBox()
        db_inner.addWidget(self.dragonborn_combo)
        self.dragonborn_group.setVisible(False)
        layout.addWidget(self.dragonborn_group)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(_scroll_wrap(outer))

    def _on_race_changed(self, current, _prev):
        if not current:
            return
        idx = current.data(Qt.ItemDataRole.UserRole)
        race = srd.get_race(idx)
        if not race:
            return

        self.subrace_list.clear()
        if not race.get("subraces"):
            none_item = QListWidgetItem("(Keine Unterrasse)")
            none_item.setData(Qt.ItemDataRole.UserRole, None)
            self.subrace_list.addItem(none_item)
        else:
            for sr in race["subraces"]:
                item = QListWidgetItem(sr["name"])
                item.setData(Qt.ItemDataRole.UserRole, sr["index"])
                self.subrace_list.addItem(item)
        # always select first row — fires _on_subrace_changed which updates the detail area
        self.subrace_list.setCurrentRow(0)

        self.half_elf_group.setVisible(idx == "half-elf")

        self.dragonborn_combo.clear()
        if idx == "dragonborn":
            for anc in race.get("draconic_ancestry", []):
                self.dragonborn_combo.addItem(
                    f"{anc['dragon']} ({anc['damage']}, {anc['breath']})", anc["dragon"]
                )
        self.dragonborn_group.setVisible(idx == "dragonborn")

    def _on_subrace_changed(self, current, _prev):
        if not current:
            return
        race_item = self.race_list.currentItem()
        if not race_item:
            return
        race = srd.get_race(race_item.data(Qt.ItemDataRole.UserRole))
        if not race:
            return
        sr_idx = current.data(Qt.ItemDataRole.UserRole)
        sr = next((s for s in race.get("subraces", []) if s["index"] == sr_idx), None)
        self.detail_area.setPlainText(self._format_race(race, sr))

    def _format_race(self, r: dict, sr: dict | None = None) -> str:
        lines = [r["name"], "=" * 40]
        lines.append(f"Geschwindigkeit: {r['speed']} ft | Größe: {r.get('size','?')}")
        lines.append("")

        # Ability bonuses: base + subrace combined
        all_bonuses = list(r.get("ability_bonuses", []))
        if sr:
            all_bonuses.extend(sr.get("ability_bonuses", []))
        if all_bonuses:
            ab_str = ", ".join(
                f"+{b['bonus']} {b['score']}"
                for b in all_bonuses
                if b["score"] not in ("choice_1", "choice_2")
            )
            if r["index"] == "half-elf":
                ab_str += ", +1 auf zwei wählbare Attribute"
            lines.append(f"Attributboni: {ab_str}")

        lines.append(f"Sprachen: {', '.join(r.get('languages', []))}")
        lines.append("")

        lines.append("Volksmerkmale:")
        for t in r.get("traits", []):
            lines.append(f"  • {t['name']}: {t['desc']}")

        if sr:
            lines.append("")
            lines.append(f"── {sr['name']} ──")
            for t in sr.get("traits", []):
                lines.append(f"  • {t['name']}: {t['desc']}")

        return "\n".join(lines)

    def selected_race(self) -> str | None:
        item = self.race_list.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def selected_subrace(self) -> str | None:
        item = self.subrace_list.currentItem()
        if not item:
            return None
        val = item.data(Qt.ItemDataRole.UserRole)
        return val if val else None

    def half_elf_choices(self) -> list[str]:
        return [cb.currentText() for cb in self.he_combos]

    def dragonborn_ancestry(self) -> str | None:
        if self.selected_race() != "dragonborn":
            return None
        data = self.dragonborn_combo.currentData()
        return data if data else self.dragonborn_combo.currentText()

    def reload(self):
        self._races = srd.get_races()
        self.race_list.clear()
        for r in self._races:
            item = QListWidgetItem(r["name"])
            item.setData(Qt.ItemDataRole.UserRole, r["index"])
            self.race_list.addItem(item)
        self.subrace_list.clear()
        self.detail_area.clear()
        self.half_elf_group.setVisible(False)
        self.dragonborn_group.setVisible(False)

    def validate(self) -> str | None:
        if not self.selected_race():
            return "Bitte eine Rasse auswählen."
        if self.selected_race() == "half-elf":
            choices = self.half_elf_choices()
            if choices[0] == choices[1]:
                return "Bitte zwei verschiedene Attribute für den Halbelf wählen."
        if self.selected_race() == "dragonborn" and not self.dragonborn_combo.currentText():
            return "Bitte eine drakonische Abstammung wählen."
        return None


class _Step2_Class(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._classes = srd.get_classes()
        self._build()

    def _build(self):
        outer = QWidget()
        layout = QVBoxLayout(outer)
        layout.setSpacing(12)
        layout.addWidget(_section("Schritt 3 – Klasse"))

        row = QHBoxLayout()

        left = QVBoxLayout()
        left.addWidget(QLabel("Klasse:"))
        self.class_list = QListWidget()
        self.class_list.setMaximumWidth(200)
        for c in self._classes:
            item = QListWidgetItem(c["name"])
            item.setData(Qt.ItemDataRole.UserRole, c["index"])
            self.class_list.addItem(item)
        self.class_list.currentItemChanged.connect(self._on_class_changed)
        left.addWidget(self.class_list)
        row.addLayout(left)

        right = QVBoxLayout()
        right.addWidget(QLabel("Details:"))
        self.detail_area = QTextEdit()
        self.detail_area.setReadOnly(True)
        right.addWidget(self.detail_area, 1)
        row.addLayout(right, 1)

        layout.addLayout(row)
        layout.addStretch()

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(_scroll_wrap(outer))

        # Starting level
        level_grp = QGroupBox("Startlevel")
        level_inner = QVBoxLayout(level_grp)
        level_row = QHBoxLayout()
        self.starting_level_spin = QSpinBox()
        self.starting_level_spin.setRange(1, 20)
        self.starting_level_spin.setValue(1)
        self.starting_level_spin.setFixedWidth(70)
        level_row.addWidget(QLabel("Level:"))
        level_row.addWidget(self.starting_level_spin)
        level_row.addStretch()
        level_inner.addLayout(level_row)
        self._level_hint = QLabel("")
        self._level_hint.setStyleSheet(f"color:{COLORS['muted']};font-size:12px;")
        self._level_hint.setWordWrap(True)
        level_inner.addWidget(self._level_hint)
        self.starting_level_spin.valueChanged.connect(self._on_level_changed)
        layout.addWidget(level_grp)

        layout.addStretch()

    def _on_class_changed(self, current, _prev):
        if not current:
            return
        cls = srd.get_class(current.data(Qt.ItemDataRole.UserRole))
        if cls:
            self.detail_area.setPlainText(self._format_class(cls))

    def _format_class(self, c: dict) -> str:
        lines = [c["name"], "=" * 40]
        lines.append(f"Trefferwürfel: d{c['hit_die']}")
        lines.append(f"Primärattribute: {', '.join(c['primary_abilities'])}")
        lines.append(f"Rettungswürfe: {', '.join(c['saving_throws'])}")
        lines.append(f"Rüstungen: {', '.join(c['armor_proficiencies']) or '–'}")
        lines.append(f"Waffen: {', '.join(c['weapon_proficiencies'])}")
        sc = c["skill_choices"]
        from_str = ', '.join(sc['from']) if sc['from'] != 'any' else 'beliebig'
        lines.append(f"Fertigkeiten: {sc['count']} aus ({from_str})")
        if c.get("spellcasting"):
            sp = c["spellcasting"]
            lines.append(f"Zauberkunst: Attribut {sp['ability']} ({sp['type']})")
        lines.append(f"Unterklasse ab Stufe: {c['subclass_level']} ({c['subclass_name']})")
        lines.append(f"Unterklassen: {', '.join(c['subclasses'])}")
        lines.append("")
        lines.append("Startausrüstung (Option A):")
        lines.append(f"  {c['starting_equipment_A']}")
        lines.append("")
        lines.append("Level-1-Fähigkeiten:")
        for f in c["features"].get("1", []):
            lines.append(f"  • {f}")
        return "\n".join(lines)

    def reload(self):
        self._classes = srd.get_classes()
        self.class_list.clear()
        for c in self._classes:
            item = QListWidgetItem(c["name"])
            item.setData(Qt.ItemDataRole.UserRole, c["index"])
            self.class_list.addItem(item)
        self.detail_area.clear()

    def selected_class(self) -> str | None:
        item = self.class_list.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def validate(self) -> str | None:
        return None if self.selected_class() else "Bitte eine Klasse auswählen."
    
    def _on_level_changed(self, value: int) -> None:
        if value > 1:
            self._level_hint.setText(
                f"Level {value}: Du wirst nach der Erstellung {value - 1}× durch den "
                f"Level-Up-Dialog geführt (HP, ASI-Auswahl etc.)."
            )
        else:
            self._level_hint.setText("")

    def starting_level(self) -> int:
        return self.starting_level_spin.value()

class _Step3_AbilityScores(QWidget):
    ABILITIES = srd.ABILITIES

    def __init__(self, parent=None):
        super().__init__(parent)
        self._method = "standard"
        self._rolled: list[int] = []
        self._build()

    def _build(self):
        outer = QWidget()
        layout = QVBoxLayout(outer)
        layout.setSpacing(12)
        layout.addWidget(_section("Schritt 4 – Attribute"))
        layout.addWidget(_hint("Wähle eine Methode und verteile deine Grundwerte (ohne Rassenbonus)."))

        # Method selector
        method_grp = QGroupBox("Methode")
        method_inner = QHBoxLayout(method_grp)
        self.rb_standard = QRadioButton("Standard-Array")
        self.rb_pointbuy = QRadioButton("Point Buy")
        self.rb_roll = QRadioButton("Würfeln")
        self.rb_standard.setChecked(True)
        for rb in (self.rb_standard, self.rb_pointbuy, self.rb_roll):
            method_inner.addWidget(rb)
        self.rb_standard.toggled.connect(lambda: self._set_method("standard"))
        self.rb_pointbuy.toggled.connect(lambda: self._set_method("pointbuy"))
        self.rb_roll.toggled.connect(lambda: self._set_method("roll"))
        layout.addWidget(method_grp)

        # Standard array assignment
        self.standard_grp = QGroupBox("Standard-Array: [15, 14, 13, 12, 10, 8] verteilen")
        standard_inner = QGridLayout(self.standard_grp)
        self.std_combos: dict[str, QComboBox] = {}
        for i, ab in enumerate(self.ABILITIES):
            standard_inner.addWidget(QLabel(f"{ab}:"), i, 0)
            cb = QComboBox()
            for v in STANDARD_ARRAY:
                cb.addItem(str(v))
            cb.setCurrentIndex(i)
            cb.currentIndexChanged.connect(self._update_mod_labels)
            standard_inner.addWidget(cb, i, 1)
            self.std_combos[ab] = cb
            mod_lbl = QLabel("")
            mod_lbl.setObjectName(f"mod_{ab}")
            standard_inner.addWidget(mod_lbl, i, 2)
        layout.addWidget(self.standard_grp)

        # Point buy
        self.pb_grp = QGroupBox(f"Point Buy: {POINT_BUY_BUDGET} Punkte")
        pb_inner = QGridLayout(self.pb_grp)
        self.pb_spins: dict[str, QSpinBox] = {}
        self.pb_cost_lbls: dict[str, QLabel] = {}
        self.pb_total_lbl = QLabel("Verwendete Punkte: 0 / 27")
        self.pb_total_lbl.setStyleSheet(f"color:{COLORS['gold']};font-weight:bold;")
        for i, ab in enumerate(self.ABILITIES):
            pb_inner.addWidget(QLabel(f"{ab}:"), i, 0)
            sp = QSpinBox()
            sp.setRange(8, 15)
            sp.setValue(8)
            sp.valueChanged.connect(self._update_pb)
            self.pb_spins[ab] = sp
            pb_inner.addWidget(sp, i, 1)
            cost_lbl = QLabel("(0 Punkte)")
            cost_lbl.setStyleSheet(f"color:{COLORS['muted']};font-size:12px;")
            self.pb_cost_lbls[ab] = cost_lbl
            pb_inner.addWidget(cost_lbl, i, 2)
            mod_lbl = QLabel("")
            mod_lbl.setObjectName(f"pb_mod_{ab}")
            pb_inner.addWidget(mod_lbl, i, 3)
        pb_inner.addWidget(self.pb_total_lbl, len(self.ABILITIES), 0, 1, 4)
        self.pb_grp.setVisible(False)
        layout.addWidget(self.pb_grp)

        # Roll
        self.roll_grp = QGroupBox("Würfeln (4d6, niedrigsten fallen lassen)")
        roll_inner = QVBoxLayout(self.roll_grp)
        self.roll_btn = QPushButton("Jetzt würfeln")
        self.roll_btn.setObjectName("primary-btn")
        self.roll_btn.clicked.connect(self._do_roll)
        roll_inner.addWidget(self.roll_btn)
        self.roll_results_lbl = QLabel("")
        self.roll_results_lbl.setStyleSheet(f"color:{COLORS['gold']};font-size:13px;")
        roll_inner.addWidget(self.roll_results_lbl)

        roll_assign = QGridLayout()
        self.roll_combos: dict[str, QComboBox] = {}
        for i, ab in enumerate(self.ABILITIES):
            roll_assign.addWidget(QLabel(f"{ab}:"), i, 0)
            cb = QComboBox()
            cb.currentIndexChanged.connect(self._update_mod_labels)
            self.roll_combos[ab] = cb
            roll_assign.addWidget(cb, i, 1)
            mod_lbl = QLabel("")
            mod_lbl.setObjectName(f"roll_mod_{ab}")
            roll_assign.addWidget(mod_lbl, i, 2)
        roll_inner.addLayout(roll_assign)
        self.roll_grp.setVisible(False)
        layout.addWidget(self.roll_grp)
        layout.addStretch()

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(_scroll_wrap(outer))
        self._update_mod_labels()

    def _set_method(self, method: str):
        self._method = method
        self.standard_grp.setVisible(method == "standard")
        self.pb_grp.setVisible(method == "pointbuy")
        self.roll_grp.setVisible(method == "roll")

    def _update_mod_labels(self):
        for ab in self.ABILITIES:
            score = self._get_score(ab)
            m = modifier(score)
            sign = "+" if m >= 0 else ""
            label_text = f"{score} ({sign}{m})"
            for prefix in ("mod_", "pb_mod_", "roll_mod_"):
                widget = self.findChild(QLabel, f"{prefix}{ab}")
                if widget:
                    color = COLORS["success"] if m >= 0 else COLORS["error"]
                    widget.setText(label_text)
                    widget.setStyleSheet(f"color:{color};font-weight:bold;")

    def _update_pb(self):
        total_cost = sum(POINT_BUY_COSTS.get(sp.value(), 0) for sp in self.pb_spins.values())
        remaining = POINT_BUY_BUDGET - total_cost
        color = COLORS["success"] if remaining >= 0 else COLORS["error"]
        self.pb_total_lbl.setText(f"Verwendete Punkte: {total_cost} / {POINT_BUY_BUDGET} (verbleibend: {remaining})")
        self.pb_total_lbl.setStyleSheet(f"color:{color};font-weight:bold;")
        for ab, sp in self.pb_spins.items():
            cost = POINT_BUY_COSTS.get(sp.value(), 0)
            self.pb_cost_lbls[ab].setText(f"({cost} Pkt)")
        self._update_mod_labels()

    def _do_roll(self):
        self._rolled = []
        for _ in range(6):
            dice = sorted(random.randint(1, 6) for _ in range(4))
            self._rolled.append(sum(dice[1:]))
        self.roll_results_lbl.setText(f"Gewürfelte Werte: {self._rolled}")
        for cb in self.roll_combos.values():
            cb.clear()
            for v in self._rolled:
                cb.addItem(str(v))
        self._update_mod_labels()

    def _get_score(self, ab: str) -> int:
        if self._method == "standard":
            return int(self.std_combos[ab].currentText())
        elif self._method == "pointbuy":
            return self.pb_spins[ab].value()
        else:
            text = self.roll_combos[ab].currentText()
            return int(text) if text else 8

    def get_scores(self) -> dict[str, int]:
        return {ab: self._get_score(ab) for ab in self.ABILITIES}

    def validate(self) -> str | None:
        if self._method == "standard":
            selected = sorted(int(self.std_combos[ab].currentText()) for ab in self.ABILITIES)
            if selected != sorted(STANDARD_ARRAY):
                return "Jeder Wert des Standard-Arrays muss genau einmal vergeben werden."
        elif self._method == "pointbuy":
            total = sum(POINT_BUY_COSTS.get(sp.value(), 0) for sp in self.pb_spins.values())
            if total > POINT_BUY_BUDGET:
                return f"Point Buy: {total} Punkte verbraucht, Maximum ist {POINT_BUY_BUDGET}."
        elif self._method == "roll":
            for ab in self.ABILITIES:
                if not self.roll_combos[ab].currentText():
                    return "Bitte erst würfeln und alle Attribute zuweisen."
        return None


class _Step4_Background(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._backgrounds = srd.get_backgrounds()
        self._build()

    def _build(self):
        outer = QWidget()
        layout = QVBoxLayout(outer)
        layout.setSpacing(12)
        layout.addWidget(_section("Schritt 5 – Hintergrund"))

        row = QHBoxLayout()
        left = QVBoxLayout()
        left.addWidget(QLabel("Hintergrund:"))
        self.bg_list = QListWidget()
        self.bg_list.setMaximumWidth(200)
        for b in self._backgrounds:
            item = QListWidgetItem(b["name"])
            item.setData(Qt.ItemDataRole.UserRole, b["index"])
            self.bg_list.addItem(item)
        self.bg_list.currentItemChanged.connect(self._on_bg_changed)
        left.addWidget(self.bg_list)
        row.addLayout(left)

        right = QVBoxLayout()
        right.addWidget(QLabel("Details:"))
        self.detail_area = QTextEdit()
        self.detail_area.setReadOnly(True)
        right.addWidget(self.detail_area, 1)
        row.addLayout(right, 1)
        layout.addLayout(row)

        # Personality customization
        custom_grp = QGroupBox("Persönlichkeit (optional anpassen)")
        cg = QGridLayout(custom_grp)
        self.personality_edit = QLineEdit()
        self.ideals_edit = QLineEdit()
        self.bonds_edit = QLineEdit()
        self.flaws_edit = QLineEdit()
        for i, (lbl, w) in enumerate([
            ("Persönlichkeitsmerkmal:", self.personality_edit),
            ("Ideal:", self.ideals_edit),
            ("Bindung:", self.bonds_edit),
            ("Schwäche:", self.flaws_edit),
        ]):
            cg.addWidget(QLabel(lbl), i, 0)
            cg.addWidget(w, i, 1)
        layout.addWidget(custom_grp)
        layout.addStretch()

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(_scroll_wrap(outer))

    def _on_bg_changed(self, current, _prev):
        if not current:
            return
        bg = srd.get_background(current.data(Qt.ItemDataRole.UserRole))
        if bg:
            self.detail_area.setPlainText(self._format_bg(bg))
            self.personality_edit.setPlaceholderText(bg["personality_traits"][0] if bg["personality_traits"] else "")
            self.ideals_edit.setPlaceholderText(bg["ideals"][0] if bg["ideals"] else "")
            self.bonds_edit.setPlaceholderText(bg["bonds"][0] if bg["bonds"] else "")
            self.flaws_edit.setPlaceholderText(bg["flaws"][0] if bg["flaws"] else "")

    def _format_bg(self, b: dict) -> str:
        lines = [b["name"], "=" * 40]
        lines.append(f"Fertigkeiten: {', '.join(b['skill_proficiencies'])}")
        if b["tool_proficiencies"]:
            lines.append(f"Werkzeuge: {', '.join(b['tool_proficiencies'])}")
        if b["languages"]:
            lines.append(f"Sprachen: {b['languages']} zusätzliche(r)")
        lines.append(f"\nMerkmal: {b['feature']['name']}")
        lines.append(b['feature']['desc'])
        lines.append(f"\nAusrüstung: {b['equipment']}")
        return "\n".join(lines)

    def reload(self):
        self._backgrounds = srd.get_backgrounds()
        self.bg_list.clear()
        for b in self._backgrounds:
            item = QListWidgetItem(b["name"])
            item.setData(Qt.ItemDataRole.UserRole, b["index"])
            self.bg_list.addItem(item)
        self.detail_area.clear()

    def selected_background(self) -> str | None:
        item = self.bg_list.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def validate(self) -> str | None:
        return None if self.selected_background() else "Bitte einen Hintergrund auswählen."


class _Step5_Skills(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._class_index: str | None = None
        self._bg_skills: list[str] = []
        self._checkboxes: dict[str, QCheckBox] = {}
        self._max_choices = 0
        self._build()

    def _build(self):
        outer = QWidget()
        layout = QVBoxLayout(outer)
        layout.setSpacing(12)
        layout.addWidget(_section("Schritt 6 – Fertigkeiten"))

        self.hint_lbl = _hint("Wähle deine Klassen-Fertigkeiten aus.")
        layout.addWidget(self.hint_lbl)

        self.skills_grp = QGroupBox("Fertigkeits-Profizienz")
        self.skills_layout = QGridLayout(self.skills_grp)
        layout.addWidget(self.skills_grp)
        layout.addStretch()

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(_scroll_wrap(outer))

    def update_for_class_and_bg(self, class_index: str, bg_skills: list[str]):
        self._class_index = class_index
        self._bg_skills = bg_skills
        self._checkboxes.clear()

        cls = srd.get_class(class_index)
        if not cls:
            return

        sc = cls["skill_choices"]
        count = sc["count"]
        options = sc["from"]
        all_skills = [s["name"] for s in srd.SKILLS]
        available = all_skills if options == "any" else options

        self.hint_lbl.setText(
            f"Wähle {count} Fertigkeiten aus der Klasse. "
            f"Fertigkeiten aus dem Hintergrund ({', '.join(bg_skills)}) sind bereits gewählt."
        )

        # Clear layout
        while self.skills_layout.count():
            item = self.skills_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._max_choices = count
        col_len = (len(srd.SKILLS) + 1) // 2
        for i, skill in enumerate(srd.SKILLS):
            col = i // col_len
            row = i % col_len
            cb = QCheckBox(skill["name"])
            is_bg = skill["name"] in bg_skills
            is_avail = skill["name"] in available or options == "any"
            cb.setEnabled(is_avail and not is_bg)
            cb.setChecked(is_bg)
            if is_bg:
                cb.setStyleSheet(f"color:{COLORS['muted']};")
            cb.stateChanged.connect(self._on_skill_toggled)
            self.skills_layout.addWidget(cb, row, col)
            self._checkboxes[skill["name"]] = cb

    def _on_skill_toggled(self, _):
        chosen = sum(1 for sk, cb in self._checkboxes.items()
                     if cb.isChecked() and sk not in self._bg_skills)
        for sk, cb in self._checkboxes.items():
            if sk in self._bg_skills:
                continue
            if not cb.isChecked():
                cb.setEnabled(chosen < self._max_choices)

    def chosen_skills(self) -> list[str]:
        return [sk for sk, cb in self._checkboxes.items() if cb.isChecked() and sk not in self._bg_skills]

    def validate(self) -> str | None:
        chosen = len(self.chosen_skills())
        if chosen != self._max_choices:
            return f"Bitte genau {self._max_choices} Klassen-Fertigkeiten wählen (aktuell: {chosen})."
        return None


class _Step6_Spells(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._class_index: str | None = None
        self._cantrip_checks: dict[str, QCheckBox] = {}
        self._spell_checks: dict[str, QCheckBox] = {}
        self._build()

    def _build(self):
        outer = QWidget()
        self._layout = QVBoxLayout(outer)
        self._layout.setSpacing(12)
        self._layout.addWidget(_section("Schritt 7 – Zauber"))
        self._hint = _hint("Diese Klasse ist kein Zauberwirker.")
        self._layout.addWidget(self._hint)

        self.cantrip_grp = QGroupBox("Zaubertricks (Cantrips)")
        self.cantrip_inner = QGridLayout(self.cantrip_grp)
        self._layout.addWidget(self.cantrip_grp)

        self.spell_grp = QGroupBox("Bekannte Zauber (Stufe 1)")
        self.spell_inner = QGridLayout(self.spell_grp)
        self._layout.addWidget(self.spell_grp)

        self._layout.addStretch()
        self.cantrip_grp.setVisible(False)
        self.spell_grp.setVisible(False)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(_scroll_wrap(outer))

    def update_for_class(self, class_index: str):
        self._class_index = class_index
        cls = srd.get_class(class_index)
        sc = cls.get("spellcasting") if cls else None

        self._cantrip_checks.clear()
        self._spell_checks.clear()
        while self.cantrip_inner.count():
            item = self.cantrip_inner.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        while self.spell_inner.count():
            item = self.spell_inner.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not sc:
            self._hint.setText("Diese Klasse ist kein Zauberwirker.")
            self.cantrip_grp.setVisible(False)
            self.spell_grp.setVisible(False)
            return

        cantrips_known = sc.get("cantrips_known", [])
        n_cantrips = cantrips_known[0] if cantrips_known else 0

        if n_cantrips > 0:
            self._hint.setText(f"Wähle {n_cantrips} Zaubertrick(s) und Stufe-1-Zauber.")
            self.cantrip_grp.setTitle(f"Zaubertricks (wähle {n_cantrips})")
            cantrips = srd.get_cantrips(class_index)
            col_len = max(1, (len(cantrips) + 1) // 2)
            for i, sp in enumerate(cantrips):
                cb = QCheckBox(sp["name"])
                cb.setToolTip(sp["desc"])
                cb.stateChanged.connect(lambda _, n=n_cantrips: self._enforce_limit(self._cantrip_checks, n))
                self._cantrip_checks[sp["name"]] = cb
                self.cantrip_inner.addWidget(cb, i % col_len, i // col_len)
            self.cantrip_grp.setVisible(True)
        else:
            self.cantrip_grp.setVisible(False)

        # Level 1 spells
        known_raw = sc.get("spells_known", [])
        n_spells = known_raw[0] if isinstance(known_raw, list) and known_raw else 0
        if sc["type"] in ("prepared", "spellbook"):
            n_spells = 0  # Prepared casters don't have a fixed "known" at lvl 1 in wizard
            self.spell_grp.setTitle("Vorbereitet-Wirker: keine feste Zauberauswahl hier")
        else:
            self.spell_grp.setTitle(f"Bekannte Zauber Stufe 1 (wähle {n_spells})")

        if n_spells > 0:
            level1_spells = srd.get_spells(class_index=class_index, level=1)
            col_len = max(1, (len(level1_spells) + 1) // 2)
            for i, sp in enumerate(level1_spells):
                cb = QCheckBox(sp["name"])
                cb.setToolTip(sp["desc"])
                cb.stateChanged.connect(lambda _, n=n_spells: self._enforce_limit(self._spell_checks, n))
                self._spell_checks[sp["name"]] = cb
                self.spell_inner.addWidget(cb, i % col_len, i // col_len)
            self.spell_grp.setVisible(True)
        else:
            self.spell_grp.setVisible(False)

    def _enforce_limit(self, checks: dict[str, QCheckBox], limit: int):
        chosen = sum(1 for cb in checks.values() if cb.isChecked())
        for cb in checks.values():
            if not cb.isChecked():
                cb.setEnabled(chosen < limit)

    def chosen_cantrips(self) -> list[str]:
        return [name for name, cb in self._cantrip_checks.items() if cb.isChecked()]

    def chosen_spells(self) -> list[str]:
        return [name for name, cb in self._spell_checks.items() if cb.isChecked()]

    def validate(self) -> str | None:
        cls = srd.get_class(self._class_index) if self._class_index else None
        sc = cls.get("spellcasting") if cls else None
        if not sc:
            return None
        cantrips_known = sc.get("cantrips_known", [])
        n_cantrips = cantrips_known[0] if cantrips_known else 0
        if n_cantrips and len(self.chosen_cantrips()) != n_cantrips:
            return f"Bitte genau {n_cantrips} Zaubertrick(s) wählen."
        return None


# ── Main Wizard Dialog ─────────────────────────────────────────────────────

class CharacterWizard(QDialog):
    STEP_TITLES = [
        "Edition & Name", "Rasse", "Klasse",
        "Attribute", "Hintergrund", "Fertigkeiten", "Zauber",
    ]

    def __init__(self, base_url: str, auth_token: str | None, parent=None):
        super().__init__(parent)
        self.base_url = base_url
        self.auth_token = auth_token
        self.setWindowTitle("Neuen Charakter erstellen")
        self.setMinimumSize(900, 680)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        # Progress bar (step labels)
        self._step_labels: list[QLabel] = []
        steps_row = QHBoxLayout()
        steps_row.setContentsMargins(16, 10, 16, 0)
        for i, title in enumerate(self.STEP_TITLES):
            lbl = QLabel(f"{i+1}. {title}")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f"color:{COLORS['muted']};font-size:11px;padding:4px;")
            self._step_labels.append(lbl)
            steps_row.addWidget(lbl)
        root.addLayout(steps_row)

        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.Shape.HLine)
        root.addWidget(sep)

        # Step stack
        self.stack = QStackedWidget()
        self.step0 = _Step0_BasicInfo()
        self.step1 = _Step1_Race()
        self.step2 = _Step2_Class()
        self.step3 = _Step3_AbilityScores()
        self.step4 = _Step4_Background()
        self.step5 = _Step5_Skills()
        self.step6 = _Step6_Spells()
        for step in (self.step0, self.step1, self.step2, self.step3,
                     self.step4, self.step5, self.step6):
            self.stack.addWidget(step)
        root.addWidget(self.stack, 1)

        # Navigation buttons
        nav = QHBoxLayout()
        nav.setContentsMargins(16, 8, 16, 12)
        self.btn_back = QPushButton("← Zurück")
        self.btn_back.setObjectName("secondary-btn")
        self.btn_back.setEnabled(False)
        self.btn_back.clicked.connect(self._go_back)

        self.error_lbl = QLabel("")
        self.error_lbl.setStyleSheet(f"color:{COLORS['error']};font-size:12px;")
        self.error_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.btn_next = QPushButton("Weiter →")
        self.btn_next.setObjectName("primary-btn")
        self.btn_next.clicked.connect(self._go_next)

        nav.addWidget(self.btn_back)
        nav.addWidget(self.error_lbl, 1)
        nav.addWidget(self.btn_next)
        root.addLayout(nav)

        self._set_step(0)

    def _set_step(self, index: int):
        self._current = index
        self.stack.setCurrentIndex(index)
        self.btn_back.setEnabled(index > 0)
        last = len(self.STEP_TITLES) - 1
        self.btn_next.setText("Charakter erstellen ✓" if index == last else "Weiter →")
        self.error_lbl.setText("")
        for i, lbl in enumerate(self._step_labels):
            if i == index:
                lbl.setStyleSheet(f"color:{COLORS['accent']};font-weight:bold;font-size:11px;padding:4px;background:{COLORS['surface']};border-radius:4px;")
            elif i < index:
                lbl.setStyleSheet(f"color:{COLORS['success']};font-size:11px;padding:4px;")
            else:
                lbl.setStyleSheet(f"color:{COLORS['muted']};font-size:11px;padding:4px;")

    def _go_back(self):
        if self._current > 0:
            self._set_step(self._current - 1)

    def _go_next(self):
        step = self.stack.currentWidget()
        err = step.validate() if hasattr(step, "validate") else None
        if err:
            self.error_lbl.setText(err)
            return
        self.error_lbl.setText("")

        if self._current == 0:
            srd.set_edition(self.step0.edition())
            self.step1.reload()
            self.step2.reload()
            self.step4.reload()
        elif self._current == 1:
            pass  # race selected
        elif self._current == 2:
            # Update skills step when class is chosen
            cls_idx = self.step2.selected_class()
            bg_idx = self.step4.selected_background()
            if cls_idx:
                self.step6.update_for_class(cls_idx)
        elif self._current == 4:
            # Update skills when background is confirmed
            bg_idx = self.step4.selected_background()
            cls_idx = self.step2.selected_class()
            bg = srd.get_background(bg_idx) if bg_idx else None
            bg_skills = bg["skill_proficiencies"] if bg else []
            if cls_idx:
                self.step5.update_for_class_and_bg(cls_idx, bg_skills)
            if cls_idx:
                self.step6.update_for_class(cls_idx)

        if self._current < len(self.STEP_TITLES) - 1:
            self._set_step(self._current + 1)
        else:
            self._finish()

    def _finish(self):
        name = self.step0.name_edit.text().strip()
        bg_idx = self.step4.selected_background()

        data = build_character_data(
            name=name,
            edition=self.step0.edition(),
            race_index=self.step1.selected_race(),
            subrace_index=self.step1.selected_subrace(),
            class_index=self.step2.selected_class(),
            background_index=bg_idx,
            alignment=self.step0.align_combo.currentText(),
            base_ability_scores=self.step3.get_scores(),
            chosen_skills=self.step5.chosen_skills(),
            chosen_cantrips=self.step6.chosen_cantrips(),
            chosen_spells=self.step6.chosen_spells(),
            half_elf_score_choices=self.step1.half_elf_choices() if self.step1.selected_race() == "half-elf" else None,
            dragonborn_ancestry=self.step1.dragonborn_ancestry(),
            personality=self.step4.personality_edit.text(),
            ideals=self.step4.ideals_edit.text(),
            bonds=self.step4.bonds_edit.text(),
            flaws=self.step4.flaws_edit.text(),
        )

        # Apply starting level (> 1) via sequential level-up dialogs
        starting_level = self.step2.starting_level()
        if starting_level > 1:
            data = self._apply_starting_level(data, starting_level)
            if data is None:
                # User cancelled the level-up flow
                return

        try:
            r = requests.post(
                f"{self.base_url}/api/characters/",
                json={"name": name, "data": data},
                headers={"Authorization": f"Bearer {self.auth_token}"},
                timeout=5,
            )
            if r.status_code == 201:
                self.accept()
            else:
                self.error_lbl.setText(r.json().get("error", "Fehler beim Speichern."))
        except Exception as e:
            self.error_lbl.setText(f"Verbindungsfehler: {e}")

    def _apply_starting_level(self, data: dict, target_level: int) -> dict | None:
        """
        Walk the character from level 1 up to target_level via LevelUpDialog.
        Returns the final data dict, or None if the user cancelled.
        """
        from src.gui.dialogs.levelup_dialog import ClassPickerDialog, LevelUpDialog

        for lvl in range(2, target_level + 1):
            cls_dlg = ClassPickerDialog(data, parent=self)
            if not cls_dlg.exec():
                return None
            class_index = cls_dlg.selected_class_index
            info = get_level_up_info(data, class_index)
            lvl_dlg = LevelUpDialog(data, class_index, parent=self)
            lvl_dlg.setWindowTitle(
                f"Startlevel: Level {info['total_level']} → {info['new_total_level']} "
                f"({lvl - 1}/{target_level - 1})"
            )
            if not lvl_dlg.exec():
                return None
            data = apply_level_up(
                data, lvl_dlg.hp_gain, class_index,
                lvl_dlg.asi_changes, lvl_dlg.feat_index, lvl_dlg.subclass_index,
            )

        return data
