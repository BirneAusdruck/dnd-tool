"""
Full character sheet view — read/edit mode.
Organized like the official DnD character sheet.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QSpinBox, QGroupBox, QScrollArea, QFrame,
    QPushButton, QTabWidget, QTextEdit, QCheckBox, QMessageBox,
    QSizePolicy, QSplitter, QSpacerItem, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

import requests

from src.client.gui.theme import COLORS
from src.client.gui import assets
from src.shared.services.character_builder_service import CharacterBuilderService
from src.shared.services.level_up_service import LevelUpService
from src.shared.services.race_service import RaceService
from src.shared.services.background_service import BackgroundService
from src.shared.services.class_service import ClassService
from src.shared.services.feat_service import FeatService
from src.shared.services.item_service import ItemService
from src.shared.services.srd_constants import SRDConstants


def _fmt_mod(val: int) -> str:
    return f"+{val}" if val >= 0 else str(val)


def _build_class_line(basics: dict) -> str:
    """Build the full character subtitle: 'Level N  Rasse  Klasse A / Klasse B  •  Hintergrund  •  Gesinnung'."""
    race_name = (RaceService.get(basics.get("race", "")) or {}).get("name", basics.get("race", "?"))
    bg_name = (BackgroundService.get(basics.get("background", "")) or {}).get("name", basics.get("background", "?"))
    alignment = basics.get("alignment", "?")
    total_level = basics.get("level", 1)

    classes = basics.get("classes", [])
    if classes:
        parts = []
        for c in classes:
            cls_name = (ClassService.get_raw(c["class_index"]) or {}).get("name", c["class_index"])
            sub = f" ({c['subclass']})" if c.get("subclass") else ""
            parts.append(f"{cls_name}{sub} {c['level']}")
        class_str = " / ".join(parts)
    else:
        cls_name = (ClassService.get_raw(basics.get("class", "")) or {}).get("name", basics.get("class", "?"))
        class_str = cls_name

    return f"Level {total_level}  {race_name}  {class_str}  •  {bg_name}  •  {alignment}"


def _header_label(text: str, size: int = 11) -> QLabel:
    lbl = QLabel(text.upper())
    lbl.setStyleSheet(f"color:{COLORS['muted']};font-size:{size}px;letter-spacing:1px;")
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return lbl


def _value_label(text: str, size: int = 20, color: str | None = None) -> QLabel:
    lbl = QLabel(text)
    col = color or COLORS["text"]
    lbl.setStyleSheet(f"color:{col};font-size:{size}px;font-weight:bold;")
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return lbl


def _box(inner: QWidget, title: str = "") -> QGroupBox:
    grp = QGroupBox(title)
    layout = QVBoxLayout(grp)
    layout.setContentsMargins(8, 8, 8, 8)
    layout.addWidget(inner)
    return grp


# ── Ability Score Block ────────────────────────────────────────────────────

class _AbilityBlock(QWidget):
    def __init__(self, ability: str, score: int, icon_path : str | None = None, parent=None):
        super().__init__(parent)
        self.ability = ability
        self.setFixedWidth(144)
        layout = QVBoxLayout()
        layout_inner = QHBoxLayout(self)
        layout_inner.addLayout(layout)
        layout.setSpacing(2)
        layout.setContentsMargins(4, 4, 4, 4)
        self.setStyleSheet(
            f"background:{COLORS['surface']};border:1px solid {COLORS['border']};"
            f"border-radius:8px;"
        )

        ab_lbl = QLabel(ability)
        ab_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ab_lbl.setStyleSheet(f"color:{COLORS['muted']};font-size:10px;letter-spacing:1px;border:none;background:transparent;")

        m = (score - 10) // 2
        self.mod_lbl = QLabel(_fmt_mod(m))
        self.mod_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        col = COLORS["success"] if m >= 0 else COLORS["error"]
        self.mod_lbl.setStyleSheet(f"color:{col};font-size:24px;font-weight:bold;border:none;background:transparent;")

        self.score_lbl = QLabel(str(score))
        self.score_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score_lbl.setStyleSheet(f"color:{COLORS['subtext']};font-size:13px;border:none;background:transparent;")

        if icon_path:
            icon_lbl = QLabel()
            pixmap = QIcon(assets.resolve(icon_path)).pixmap(64, 64)
            icon_lbl.setPixmap(pixmap)
            icon_lbl.setFixedSize(64, 64)
            icon_lbl.setStyleSheet("background:transparent;")
            layout_inner.addWidget(icon_lbl)
        layout.addWidget(ab_lbl)
        layout.addWidget(self.mod_lbl)
        layout.addWidget(self.score_lbl)


# ── Skill Row ──────────────────────────────────────────────────────────────

class _SkillRow(QWidget):
    def __init__(self, skill_name: str, ability: str, bonus: int, proficient: bool, icon_path: str | None = None, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 1, 4, 1)
        layout.setSpacing(6)

        dot = QLabel("●" if proficient else "○")
        dot.setFixedWidth(14)
        col = COLORS["success"] if proficient else COLORS["muted"]
        dot.setStyleSheet(f"color:{col};font-size:12px;background:transparent;")

        bonus_lbl = QLabel(_fmt_mod(bonus))
        bonus_lbl.setFixedWidth(36)
        b_col = COLORS["text"] if proficient else COLORS["subtext"]
        bonus_lbl.setStyleSheet(f"color:{b_col};font-size:12px;font-weight:{'bold' if proficient else 'normal'};background:transparent;")

        name_lbl = QLabel(f"{skill_name}")
        name_lbl.setStyleSheet(f"color:{COLORS['subtext']};font-size:14px;background:transparent;")

        ab_lbl = QLabel(f"({ability})")
        ab_lbl.setStyleSheet(f"color:{COLORS['muted']};font-size:11px;background:transparent;")
        ab_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        if icon_path:
            icon_lbl = QLabel()
            # pixmap = QIcon(assets.resolve(icon_path)).pixmap(48, 48)
            pixmap = assets.recolored_icon(icon_path, "#b99530").pixmap(48,48)
            icon_lbl.setPixmap(pixmap)
            icon_lbl.setFixedSize(48, 48)
            icon_lbl.setStyleSheet("background:transparent;")
            layout.addWidget(icon_lbl)

        layout.addWidget(dot)
        layout.addWidget(bonus_lbl)
        layout.addWidget(name_lbl, 1)
        layout.addWidget(ab_lbl)


# ── Main Character Sheet Dialog ────────────────────────────────────────────

class CharacterSheet(QDialog):
    def __init__(self, char: dict, base_url: str, auth_token: str | None, parent=None):
        super().__init__(parent)
        self.char = char
        self.base_url = base_url
        self.auth_token = auth_token
        self._data = char.get("data", {})
        self._derived = CharacterBuilderService.derive_sheet_values(self._data) if self._data.get("ability_scores") else {}

        basics = self._data.get("basics", {})
        self.setWindowTitle(f"Charakterbogen – {char.get('name', '?')}")
        self.setMinimumSize(1050, 800)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        # ── Header bar ──
        header = QWidget()
        header.setStyleSheet(f"background:{COLORS['sidebar']};")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(16, 10, 16, 10)

        basics = self._data.get("basics", {})

        name_lbl = QLabel(self.char.get("name", "?"))
        name_lbl.setStyleSheet(f"color:{COLORS['text']};font-size:20px;font-weight:bold;")
        self._sub_lbl = QLabel(_build_class_line(basics))
        self._sub_lbl.setStyleSheet(f"color:{COLORS['subtext']};font-size:13px;")

        info_col = QVBoxLayout()
        info_col.addWidget(name_lbl)
        info_col.addWidget(self._sub_lbl)
        h_layout.addLayout(info_col, 1)

        self._prof_lbl = QLabel(f"Profizienzbonus: {_fmt_mod(self._derived.get('proficiency_bonus', 2))}")
        self._prof_lbl.setStyleSheet(f"color:{COLORS['gold']};font-weight:bold;font-size:13px;")
        h_layout.addWidget(self._prof_lbl)

        # Level-Up / Level-Down buttons
        self._btn_levelup = QPushButton("Level Up ↑")
        self._btn_levelup.setObjectName("primary-btn")
        self._btn_levelup.setFixedWidth(120)
        self._btn_levelup.setIcon(QIcon(assets.resolve(assets.ICONS_UTIL["build"])))
        self._btn_levelup.setEnabled(LevelUpService.can_level_up(self._data))
        self._btn_levelup.clicked.connect(self._do_level_up)
        h_layout.addWidget(self._btn_levelup)

        self._btn_leveldown = QPushButton("Level ↓")
        self._btn_leveldown.setObjectName("secondary-btn")
        self._btn_leveldown.setFixedWidth(100)
        self._btn_leveldown.setIcon(QIcon(assets.resolve(assets.ICONS_UTIL["cross"])))
        self._btn_leveldown.setEnabled(LevelUpService.can_level_down(self._data))
        self._btn_leveldown.setStyleSheet(
            f"QPushButton{{color:{COLORS['error']};background:{COLORS['surface']};"
            f"border:1px solid {COLORS['error']};border-radius:6px;padding:6px;}}"
        )
        self._btn_leveldown.clicked.connect(self._do_level_down)
        h_layout.addWidget(self._btn_leveldown)

        root.addWidget(header)

        # ── Tab widget ──
        self.tabs = QTabWidget()
        self._rebuild_tabs()
        root.addWidget(self.tabs, 1)

        # ── Footer ──
        footer = QHBoxLayout()
        footer.setContentsMargins(12, 6, 12, 8)
        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet(f"color:{COLORS['muted']};font-size:12px;")
        btn_save = QPushButton("Speichern")
        btn_save.setObjectName("primary-btn")
        btn_save.clicked.connect(self._save)
        footer.addWidget(self.status_lbl, 1)
        footer.addWidget(btn_save)
        root.addLayout(footer)

    # ── Tab helpers ───────────────────────────────────────────────────────

    def _rebuild_tabs(self) -> None:
        self.tabs.clear()
        self.tabs.addTab(self._build_main_tab(),        QIcon(assets.resolve(assets.ICONS_GAME["character"])), "Hauptblatt")
        self.tabs.addTab(self._build_combat_tab(),      QIcon(assets.resolve(assets.ICONS_GAME["combat"])),    "Kampf & HP")
        self.tabs.addTab(self._build_spells_tab(),      QIcon(assets.resolve(assets.ICONS_GAME["spell"])),     "Zauber")
        self.tabs.addTab(self._build_features_tab(),    QIcon(assets.resolve(assets.ICONS_UTIL["star"])),      "Merkmale")
        self.tabs.addTab(self._build_traits_tab(),      QIcon(assets.resolve(assets.ICONS_ENTITY["person"])),  "Persönlichkeit")
        self.tabs.addTab(self._build_inventory_tab(),   QIcon(assets.resolve(assets.ICONS_ENTITY["loot"])),    "Inventar")
        self.tabs.addTab(self._build_equipment_tab(),   QIcon(assets.resolve(assets.ICONS_ENTITY["armor"])),   "Ausrüstung")

    def _update_header(self) -> None:
        basics = self._data.get("basics", {})
        self._sub_lbl.setText(_build_class_line(basics))
        self._prof_lbl.setText(
            f"Profizienzbonus: {_fmt_mod(self._derived.get('proficiency_bonus', 2))}"
        )
        self._btn_levelup.setEnabled(LevelUpService.can_level_up(self._data))
        self._btn_leveldown.setEnabled(LevelUpService.can_level_down(self._data))

    # ── Level-Up / Level-Down ─────────────────────────────────────────────

    def _do_level_up(self) -> None:
        from src.client.gui.dialogs.levelup_dialog import ClassPickerDialog, LevelUpDialog

        if not LevelUpService.can_level_up(self._data):
            return
        
        cls_dlg = ClassPickerDialog(self._data, parent=self)
        if not cls_dlg.exec():
            return

        class_index = cls_dlg.selected_class_index
        lvl_dlg = LevelUpDialog(self._data, class_index, parent=self)
        if not lvl_dlg.exec():
            return
        new_data = LevelUpService.apply_level_up(
            self._data, lvl_dlg.hp_gain, class_index,
            lvl_dlg.asi_changes, lvl_dlg.feat_index, lvl_dlg.subclass_index,
        )
        self._apply_and_save(new_data, f"Level Up! Jetzt Level {new_data['basics']['level']} ✓")

    def _do_level_down(self) -> None:
        from src.client.gui.dialogs.levelup_dialog import LevelDownDialog
        if not LevelUpService.can_level_down(self._data):
            return
        dlg = LevelDownDialog(self._data, parent=self)
        if not dlg.exec():
            return
        new_data = LevelUpService.apply_level_down(self._data)
        self._apply_and_save(new_data, f"Level gesenkt auf Level {new_data['basics']['level']} ✓")

    def _apply_and_save(self, new_data: dict, success_msg: str) -> None:
        try:
            r = requests.put(
                f"{self.base_url}/api/characters/{self.char['id']}",
                json={"name": self.char["name"], "data": new_data},
                headers={"Authorization": f"Bearer {self.auth_token}"},
                timeout=5,
            )
            if r.status_code == 200:
                self._data = new_data
                self.char["data"] = new_data
                self._derived = CharacterBuilderService.derive_sheet_values(self._data)
                self._update_header()
                self._rebuild_tabs()
                self.status_lbl.setText(success_msg)
                self.status_lbl.setStyleSheet(f"color:{COLORS['success']};font-size:12px;")
            else:
                msg = r.json().get("error", "Fehler beim Speichern.")
                self.status_lbl.setText(msg)
                self.status_lbl.setStyleSheet(f"color:{COLORS['error']};font-size:12px;")
        except Exception as e:
            self.status_lbl.setText(str(e))
            self.status_lbl.setStyleSheet(f"color:{COLORS['error']};font-size:12px;")

    # ── Main tab: Ability scores, Skills, Saves ────────────────────────────

    def _build_main_tab(self) -> QWidget:
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        scores = self._data.get("ability_scores", {})
        profs = self._data.get("proficiencies", {})
        derived = self._derived

        # Column 1: Ability scores
        ab_col = QVBoxLayout()
        ab_grp = QGroupBox("Attribute")
        # ab_grp.setMinimumWidth(200)
        ab_inner = QVBoxLayout(ab_grp)
        ab_inner.setSpacing(6)
        for ab in SRDConstants.ABILITIES:
            block = _AbilityBlock(ab, scores.get(ab, 10), assets.ICONS_ABILITY[ab])
            ab_inner.addWidget(block)
        ab_col.addWidget(ab_grp)
        ab_col.addStretch()
        layout.addLayout(ab_col)

        # Column 2: Saving Throws + Inspiration + Passive Perception
        st_col = QVBoxLayout()

        inspiration_grp = QGroupBox("Inspiration")
        insp_inner = QHBoxLayout(inspiration_grp)
        self.inspiration_cb = QCheckBox("Aktiv")
        insp_inner.addWidget(self.inspiration_cb)
        st_col.addWidget(inspiration_grp)

        save_grp = QGroupBox("Rettungswürfe")
        save_inner = QVBoxLayout(save_grp)
        save_inner.setSpacing(2)
        for ab in SRDConstants.ABILITIES:
            val = derived.get("saving_throws", {}).get(ab, 0)
            proficient = ab in profs.get("saving_throws", [])
            row = _SkillRow(ab, ab, val, proficient, assets.ICONS_ABILITY[ab])
            save_inner.addWidget(row)
        st_col.addWidget(save_grp)

        pp_grp = QGroupBox("Passive Wahrnehmung")
        pp_inner = QHBoxLayout(pp_grp)
        pp_lbl = _value_label(str(derived.get("passive_perception", 10)), size=22, color=COLORS["gold"])
        pp_inner.addWidget(pp_lbl)
        st_col.addWidget(pp_grp)

        st_col.addStretch()
        layout.addLayout(st_col)

        # Column 3: Skills
        skill_scroll = QScrollArea()
        skill_scroll.setWidgetResizable(True)
        skill_scroll.setFrameShape(QFrame.Shape.NoFrame)
        skill_scroll.setMinimumWidth(260)

        skill_container = QWidget()
        skill_layout = QVBoxLayout(skill_container)
        skill_layout.setSpacing(2)
        skill_layout.setContentsMargins(4, 4, 4, 4)

        skill_container_left = QWidget()
        skill_layout_left = QVBoxLayout(skill_container_left)
        skill_layout_left.setSpacing(2)
        skill_layout_left.setContentsMargins(4, 4, 4, 4)

        skill_container_right = QWidget()
        skill_layout_right = QVBoxLayout(skill_container_right)
        skill_layout_right.setSpacing(2)
        skill_layout_right.setContentsMargins(4, 4, 4, 4)

        skill_hdr = QLabel("Fertigkeiten")
        skill_hdr.setStyleSheet(f"color:{COLORS['subtext']};font-size:13px;font-weight:bold;border:none;")
        skill_layout.addWidget(skill_hdr)
        
        counter = 0
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(
            f"QSplitter::handle{{background:{COLORS['border']};width:1px;}}"
        )

        for skill in SRDConstants.SKILLS:
            val = derived.get("skills", {}).get(skill["name"], 0)
            proficient = skill["name"] in profs.get("skills", [])
            row = _SkillRow(skill["name"], skill["ability"], val, proficient, assets.ICONS_SKILL[skill["name"]])
            if counter < len(SRDConstants.SKILLS) / 2:
                skill_layout_left.addWidget(row)
            else:
                skill_layout_right.addWidget(row)
            counter+=1

        splitter.addWidget(skill_container_left)
        splitter.addWidget(skill_container_right)
        # skill_layout.addStretch()
        skill_layout.addWidget(splitter)
        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        # spacer.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        skill_layout.addSpacerItem(spacer)
        skill_scroll.setWidget(skill_container)
        layout.addWidget(skill_scroll, 1)

        return w

    # ── Combat tab ────────────────────────────────────────────────────────

    def _build_combat_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        hp = self._data.get("hp", {})
        scores = self._data.get("ability_scores", {})

        # HP row
        hp_grp = QGroupBox("Trefferpunkte")
        hp_grid = QGridLayout(hp_grp)
        hp_grid.setSpacing(12)

        for col, (lbl_txt, key, icon_p) in enumerate([
            ("Maximum",  "max",     assets.ICONS_HP["full"]),
            ("Aktuell",  "current", assets.ICONS_HP["blood"]),
            ("Temporär", "temp",    assets.ICONS_HP["temp"]),
        ]):
            ic = QLabel()
            ic.setPixmap(QIcon(assets.resolve(icon_p)).pixmap(24, 24))
            ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ic.setStyleSheet("background:transparent;")
            hp_grid.addWidget(ic, 0, col)
            hp_grid.addWidget(_header_label(lbl_txt), 1, col)
            sp = QSpinBox()
            sp.setRange(0, 999)
            sp.setValue(hp.get(key, 0))
            sp.setStyleSheet(f"font-size:18px;color:{COLORS['text']};background:{COLORS['bg']};border:1px solid {COLORS['border']};border-radius:4px;")
            setattr(self, f"hp_{key}", sp)
            hp_grid.addWidget(sp, 2, col)
        layout.addWidget(hp_grp)

        # Combat stats row
        combat_grp = QGroupBox("Kampfwerte")
        combat_grid = QGridLayout(combat_grp)
        combat_grid.setSpacing(12)

        derived = self._derived
        basics = self._data.get("basics", {})
        eq = self._data.get("equipment", {})
        race = RaceService.get(basics.get("race", ""))
        speed = race["speed"] if race else 30
        ac = CharacterBuilderService.calc_ac(
            eq.get("armor"),
            scores.get("DEX", 10),
            eq.get("shield", False),
            basics.get("class", ""),
            scores.get("STR", 10),
            scores.get("WIS", 10),
            scores.get("CON", 10),
        )

        stats = [
            ("RK",             str(ac),                                            assets.ICONS_ATTRIBUTE["ac"]),
            ("Initiative",     _fmt_mod(derived.get("initiative", 0)),             assets.ICONS_COMBAT["initiative"]),
            ("Geschwindigkeit",f"{speed} ft",                                      assets.ICONS_MOVEMENT["walking"]),
            ("Trefferwürfel",  self._data.get("hit_dice", {}).get("total", "1d8"), assets.ICONS_DICE["d20"]),
        ]
        for col, (lbl, val, icon_p) in enumerate(stats):
            ic = QLabel()
            ic.setPixmap(QIcon(assets.resolve(icon_p)).pixmap(24, 24))
            ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ic.setStyleSheet("background:transparent;")
            combat_grid.addWidget(ic, 0, col)
            combat_grid.addWidget(_header_label(lbl), 1, col)
            combat_grid.addWidget(_value_label(val, size=18, color=COLORS["gold"]), 2, col)
        layout.addWidget(combat_grp)

        # Death saves
        death_grp = QGroupBox("Todesrettungswürfe")
        death_inner = QHBoxLayout(death_grp)
        ds = self._data.get("death_saves", {})

        success_inner = QVBoxLayout()
        success_inner.addWidget(QLabel("Erfolge:"))
        suc_row = QHBoxLayout()
        self.death_success_cbs = []
        for _ in range(3):
            cb = QCheckBox()
            suc_row.addWidget(cb)
            self.death_success_cbs.append(cb)
        success_inner.addLayout(suc_row)
        death_inner.addLayout(success_inner)

        fail_inner = QVBoxLayout()
        fail_inner.addWidget(QLabel("Misserfolge:"))
        fail_row = QHBoxLayout()
        self.death_fail_cbs = []
        for _ in range(3):
            cb = QCheckBox()
            fail_row.addWidget(cb)
            self.death_fail_cbs.append(cb)
        fail_inner.addLayout(fail_row)
        death_inner.addLayout(fail_inner)
        layout.addWidget(death_grp)

        # Currency
        curr_grp = QGroupBox("Währung")
        curr_grid = QGridLayout(curr_grp)
        currency = self._data.get("equipment", {}).get("currency", {})
        self.currency_spins: dict[str, QSpinBox] = {}
        for i, (key, lbl) in enumerate([("cp","KP"),("sp","SP"),("ep","EP"),("gp","GP"),("pp","PP")]):
            curr_grid.addWidget(_header_label(lbl), 0, i)
            sp = QSpinBox()
            sp.setRange(0, 999999)
            sp.setValue(currency.get(key, 0))
            sp.setStyleSheet(f"color:{COLORS['gold']};background:{COLORS['bg']};border:1px solid {COLORS['border']};border-radius:4px;font-size:14px;")
            curr_grid.addWidget(sp, 1, i)
            self.currency_spins[key] = sp
        layout.addWidget(curr_grp)

        layout.addStretch()
        return w

    # ── Spells tab ────────────────────────────────────────────────────────

    def _build_spells_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)

        sc = self._data.get("spellcasting")
        basics = self._data.get("basics", {})
        classes_list = basics.get("classes", [])
        total_level = basics.get("level", 1)

        # Find any spellcasting class for info header
        primary_caster_idx = next(
            (c["class_index"] for c in classes_list
             if ClassService.get_raw(c["class_index"]) and ClassService.get_raw(c["class_index"]).get("spellcasting")),
            basics.get("class", ""),
        )
        cls = ClassService.get_raw(primary_caster_idx)
        cls_sc = cls.get("spellcasting") if cls else None

        if not sc or not cls_sc:
            lbl = QLabel("Diese Klasse wirkt keine Zauber.")
            lbl.setStyleSheet(f"color:{COLORS['muted']};font-style:italic;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(lbl)
            layout.addStretch()
            return w

        scores = self._data.get("ability_scores", {})
        ab = cls_sc["ability"]
        ab_mod = (scores.get(ab, 10) - 10) // 2
        prof = CharacterBuilderService.proficiency_bonus(total_level)
        save_dc = 8 + prof + ab_mod
        spell_attack = prof + ab_mod

        # Cantrip scaling tier (based on total character level)
        tier = LevelUpService.get_cantrip_scaling_tier(total_level)
        tier_range = {1: "1–4", 2: "5–10", 3: "11–16", 4: "17–20"}[tier]

        info_grp = QGroupBox("Zauber-Info")
        info_inner = QGridLayout(info_grp)
        _spell_icons = [
            assets.ICONS_ABILITY.get(ab),
            assets.ICONS_ATTRIBUTE["saving-throw"],
            assets.ICONS_D20TEST["attacking"],
            assets.ICONS_DICE["d20"],
        ]
        for col, ((hdr, val), icon_p) in enumerate(zip([
            ("Zauberwirken-Attribut", ab),
            ("Rettungswurf-SG", str(save_dc)),
            ("Zauberangriff", _fmt_mod(spell_attack)),
            ("Zaubertrick-Stufe", f"{tier}× (Lvl {tier_range})"),
        ], _spell_icons)):
            if icon_p:
                ic = QLabel()
                ic.setPixmap(QIcon(assets.resolve(icon_p)).pixmap(24, 24))
                ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
                ic.setStyleSheet("background:transparent;")
                info_inner.addWidget(ic, 0, col)
            info_inner.addWidget(_header_label(hdr), 1, col)
            info_inner.addWidget(_value_label(val, size=16, color=COLORS["gold"]), 2, col)
        layout.addWidget(info_grp)

        # Known cantrips + spells
        known_grp = QGroupBox("Bekannte Zauber")
        known_inner = QVBoxLayout(known_grp)
        cantrips = sc.get("cantrips", [])
        spells = sc.get("spells_known", [])
        if cantrips:
            known_inner.addWidget(QLabel(f"Zaubertricks: {', '.join(cantrips)}"))
        if spells:
            known_inner.addWidget(QLabel(f"Zauber: {', '.join(spells)}"))
        if not cantrips and not spells:
            known_inner.addWidget(QLabel("Noch keine Zauber ausgewählt."))
        layout.addWidget(known_grp)

        # Spell slots — combined for multiclassers, per-class for single-class
        multiclass = LevelUpService.is_multiclass_spellcaster(classes_list)
        if multiclass:
            combined_level = LevelUpService.get_combined_caster_level(classes_list)
            slots = LevelUpService.get_multiclass_spell_slots(combined_level)
            slots_title = "Kombinierte Zauberplätze (Multiclass)"
        else:
            _cls = ClassService.get_raw(primary_caster_idx)
            _sc_slots = (_cls or {}).get("spellcasting", {}) or {}
            _raw = _sc_slots.get("slots", [])
            slots = list(_raw[min(total_level - 1, len(_raw) - 1)]) if _raw else []
            slots_title = "Zauberplätze"

        if slots:
            slots_grp = QGroupBox(slots_title)
            slots_inner = QGridLayout(slots_grp)
            for i, count in enumerate(slots):
                if count > 0:
                    slots_inner.addWidget(_header_label(f"Grad {i+1}"), 0, i)
                    slots_inner.addWidget(_value_label(str(count), size=14), 1, i)
            layout.addWidget(slots_grp)

        # Warlock pact slots (always separate)
        warlock_entry = next((c for c in classes_list if c["class_index"] == "warlock"), None)
        if warlock_entry:
            pact_count, pact_level = LevelUpService.get_pact_slots(warlock_entry["level"])
            if pact_count:
                pact_grp = QGroupBox("Pakt-Magie (Warlock)")
                pact_inner = QHBoxLayout(pact_grp)
                wl_icon = assets.ICONS_CLASS.get("warlock")
                if wl_icon:
                    wl_ic = QLabel()
                    wl_ic.setPixmap(QIcon(assets.resolve(wl_icon)).pixmap(24, 24))
                    wl_ic.setStyleSheet("background:transparent;")
                    pact_inner.addWidget(wl_ic)
                pact_lbl = _value_label(
                    f"{pact_count}× Grad {pact_level}", size=14, color=COLORS["accent"]
                )
                pact_inner.addWidget(pact_lbl)
                pact_inner.addStretch()
                layout.addWidget(pact_grp)

        layout.addStretch()
        return w

    # ── Features tab ──────────────────────────────────────────────────────

    def _build_features_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)

        basics = self._data.get("basics", {})
        level = basics.get("level", 1)
        class_idx = basics.get("class", "")
        _cls_data = ClassService.get_raw(class_idx)
        features: list[str] = []
        if _cls_data:
            for _lvl in range(1, level + 1):
                features.extend(_cls_data["features"].get(str(_lvl), []))

        feat_grp = QGroupBox(f"Klassenfähigkeiten (Level 1–{level})")
        feat_inner = QVBoxLayout(feat_grp)
        if features:
            for f in features:
                lbl = QLabel(f"• {f}")
                lbl.setWordWrap(True)
                lbl.setStyleSheet(f"color:{COLORS['subtext']};font-size:13px;")
                feat_inner.addWidget(lbl)
        else:
            feat_inner.addWidget(QLabel("Keine Einträge."))
        layout.addWidget(feat_grp)

        # Feats
        feat_indices = basics.get("feats", [])
        if feat_indices:
            feats_grp = QGroupBox("Talente (Feats)")
            feats_inner = QVBoxLayout(feats_grp)
            for fidx in feat_indices:
                feat = FeatService.get_raw(fidx)
                if feat:
                    name_lbl = QLabel(f"• {feat['name']}")
                    name_lbl.setStyleSheet(
                        f"color:{COLORS['gold']};font-size:13px;font-weight:bold;"
                    )
                    feats_inner.addWidget(name_lbl)
                    for b in feat.get("benefits", []):
                        b_lbl = QLabel(f"  {b}")
                        b_lbl.setWordWrap(True)
                        b_lbl.setStyleSheet(f"color:{COLORS['subtext']};font-size:12px;")
                        feats_inner.addWidget(b_lbl)
            layout.addWidget(feats_grp)

        # Racial traits
        race_idx = basics.get("race", "")
        subrace_idx = basics.get("subrace")
        race = RaceService.get(race_idx)
        if race:
            race_grp = QGroupBox(f"Volksmerkmale – {race['name']}")
            race_inner = QVBoxLayout(race_grp)
            traits = list(race.get("traits", []))
            if subrace_idx:
                sr = RaceService.get_subrace(race_idx, subrace_idx)
                if sr:
                    traits.extend(sr.get("traits", []))
            for t in traits:
                lbl = QLabel(f"• {t['name']}: {t['desc']}")
                lbl.setWordWrap(True)
                lbl.setStyleSheet(f"color:{COLORS['subtext']};font-size:12px;")
                race_inner.addWidget(lbl)
            layout.addWidget(race_grp)

        layout.addStretch()
        return w

    # ── Traits tab ────────────────────────────────────────────────────────

    def _build_traits_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        traits = self._data.get("traits", {})
        self.trait_edits: dict[str, QTextEdit] = {}
        for key, label in [
            ("personality", "Persönlichkeitsmerkmal"),
            ("ideals", "Ideal"),
            ("bonds", "Bindung"),
            ("flaws", "Schwäche"),
        ]:
            grp = QGroupBox(label)
            grp_inner = QVBoxLayout(grp)
            te = QTextEdit()
            te.setPlainText(traits.get(key, ""))
            te.setFixedHeight(70)
            grp_inner.addWidget(te)
            self.trait_edits[key] = te
            layout.addWidget(grp)

        notes_grp = QGroupBox("Notizen")
        notes_inner = QVBoxLayout(notes_grp)
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlainText(self._data.get("notes", ""))
        notes_inner.addWidget(self.notes_edit)
        layout.addWidget(notes_grp, 1)

        return w

    # ── Inventory tab ─────────────────────────────────────────────────────

    def _build_inventory_tab(self) -> QWidget:
        """Zeigt das Inventar des Charakters und erlaubt das Hinzufügen/Entfernen von Gegenständen."""
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # Header-Zeile mit Add-Button
        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("Inventar"))
        top_row.addStretch()
        btn_add = QPushButton("+ Gegenstand hinzufügen")
        btn_add.setObjectName("primary-btn")
        btn_add.clicked.connect(self._on_inventory_add)
        top_row.addWidget(btn_add)
        layout.addLayout(top_row)

        # Splitter: links = Item-Liste, rechts = Detail
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Links: Inventar-Liste
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        self._inv_list = QListWidget()
        self._inv_list.currentItemChanged.connect(self._on_inventory_selected)
        left_layout.addWidget(self._inv_list)

        # Buttons unter der Liste
        btn_row = QHBoxLayout()
        self._btn_inv_remove = QPushButton("Entfernen")
        self._btn_inv_remove.setObjectName("secondary-btn")
        self._btn_inv_remove.setEnabled(False)
        self._btn_inv_remove.clicked.connect(self._on_inventory_remove)
        btn_row.addWidget(self._btn_inv_remove)
        btn_row.addStretch()
        left_layout.addLayout(btn_row)

        splitter.addWidget(left)

        # Rechts: Detail-Ansicht
        self._inv_detail = QTextEdit()
        self._inv_detail.setReadOnly(True)
        self._inv_detail.setPlaceholderText("← Gegenstand auswählen für Details")
        splitter.addWidget(self._inv_detail)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        layout.addWidget(splitter, 1)

        self._refresh_inventory_list()
        return w

    def _refresh_inventory_list(self) -> None:
        if not hasattr(self, "_inv_list"):
            return
        self._inv_list.clear()
        inventory = self._data.get("inventory", [])
        type_labels = {"weapon": "Waffe", "armor": "Rüstung", "equipment": "Ausrüstung", "magic-item": "Magisch"}
        for entry in inventory:
            item_type = entry.get("item_type", "")
            qty = entry.get("quantity", 1)
            equipped = " [ausgerüstet]" if entry.get("equipped") else ""
            attuned = " [eingestimmt]" if entry.get("attuned") else ""
            label = f"[{type_labels.get(item_type, item_type)}] {entry.get('name', entry.get('item_index', '?'))} ×{qty}{equipped}{attuned}"
            list_item = QListWidgetItem(label)
            list_item.setData(Qt.ItemDataRole.UserRole, entry)
            self._inv_list.addItem(list_item)

    def _on_inventory_selected(self, current, _prev) -> None:
        if not current:
            self._btn_inv_remove.setEnabled(False)
            self._inv_detail.clear()
            return
        self._btn_inv_remove.setEnabled(True)
        entry = current.data(Qt.ItemDataRole.UserRole)
        idx = entry.get("item_index", "")
        item_type = entry.get("item_type", "")
        lines = []
        item = None
        if item_type == "weapon":
            item = ItemService.get_weapon_raw(idx)
            if item:
                lines.append(f"<b>{item['name']}</b> ({item['category']})")
                if item.get("damage"):
                    lines.append(f"Schaden: {item['damage']} {item['damage_type']}")
                if item.get("damage_versatile"):
                    lines.append(f"Vielseitig: {item['damage_versatile']}")
                if item.get("range"):
                    lines.append(f"Reichweite: {item['range']}")
                if item.get("properties"):
                    lines.append(f"Eigenschaften: {', '.join(item['properties'])}")
                lines.append(f"Gewicht: {item['weight']} lb  |  Kosten: {item['cost']}")
        elif item_type == "armor":
            item = ItemService.get_armor_raw(idx)
            if item:
                lines.append(f"<b>{item['name']}</b> ({item['category']} armor)")
                ac_str = str(item['base_ac'])
                if item.get("dex_bonus"):
                    max_d = item.get("max_dex")
                    ac_str += f" + DEX{f' (max {max_d})' if max_d is not None else ''}"
                lines.append(f"RK: {ac_str}")
                if item.get("str_requirement"):
                    lines.append(f"Stärke-Voraussetzung: {item['str_requirement']}")
                if item.get("stealth_disadvantage"):
                    lines.append("Nachteil auf Heimlichkeit")
                lines.append(f"Gewicht: {item['weight']} lb  |  Kosten: {item['cost']}")
        elif item_type == "equipment":
            item = ItemService.get_equipment_raw(idx)
            if item:
                lines.append(f"<b>{item['name']}</b> ({item['category']})")
                lines.append(f"Gewicht: {item['weight']} lb  |  Kosten: {item['cost']}")
        elif item_type == "magic-item":
            item = ItemService.get_magic_item_raw(idx)
            if item:
                lines.append(f"<b>{item['name']}</b>")
                lines.append(f"Seltenheit: {item['rarity'].capitalize()}")
                if item.get("attunement"):
                    att = item["attunement"]
                    att_str = att if isinstance(att, str) else "Ja"
                    lines.append(f"Einstimmung: {att_str}")
        if item:
            lines.append("")
            lines.append(item.get("desc", ""))
        if entry.get("notes"):
            lines.append(f"<i>Notizen: {entry['notes']}</i>")
        self._inv_detail.setHtml("<br>".join(lines))

    def _on_inventory_add(self) -> None:
        from src.client.gui.dialogs.inventory_dialog import InventoryAddDialog
        dlg = InventoryAddDialog(self._data, parent=self)
        if dlg.exec():
            inv = list(self._data.get("inventory", []))
            inv.append(dlg.result_entry)
            self._data["inventory"] = inv
            self._refresh_inventory_list()
            self.status_lbl.setText("Gegenstand hinzugefügt.")
            self.status_lbl.setStyleSheet(f"color:{COLORS['success']};font-size:12px;")

    def _on_inventory_remove(self) -> None:
        item = self._inv_list.currentItem()
        if not item:
            return
        entry = item.data(Qt.ItemDataRole.UserRole)
        inv = list(self._data.get("inventory", []))
        try:
            inv.remove(entry)
        except ValueError:
            pass
        self._data["inventory"] = inv
        self._refresh_inventory_list()

    # ── Equipment ─────────────────────────────────────────────────────────

    def _ensure_equipment_fields(self) -> None:
        eq = self._data.setdefault("equipment", {})
        if "weapon_sets" not in eq:
            eq["weapon_sets"] = [
                {"main_hand": None, "off_hand": None},
                {"main_hand": None, "off_hand": None},
            ]
        if "active_weapon_set" not in eq:
            eq["active_weapon_set"] = 0
        if "attunement_slots" not in eq:
            eq["attunement_slots"] = [None, None, None]
        if "armor_slot" not in eq:
            eq["armor_slot"] = None

    def _get_srd_item(self, entry: dict) -> dict:
        idx = entry.get("item_index", "")
        t = entry.get("item_type", "")
        if t == "weapon":     return ItemService.get_weapon_raw(idx) or {}
        if t == "armor":      return ItemService.get_armor_raw(idx) or {}
        if t == "equipment":  return ItemService.get_equipment_raw(idx) or {}
        if t == "magic-item": return ItemService.get_magic_item_raw(idx) or {}
        return {}

    def _sync_legacy_eq(self) -> None:
        eq = self._data["equipment"]
        armor_entry = eq.get("armor_slot")
        eq["armor"] = armor_entry["item_index"] if armor_entry else None
        active_ws = eq["weapon_sets"][eq.get("active_weapon_set", 0)]
        off = active_ws.get("off_hand")
        if off:
            srd_item = self._get_srd_item(off)
            eq["shield"] = srd_item.get("category") == "shield"
        else:
            eq["shield"] = False

    def _build_slot_frame(self, label: str, inv_entry: dict | None,
                          equip_fn, unequip_fn) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet(
            f"background:{COLORS['surface']};border:1px solid {COLORS['border']};"
            f"border-radius:6px;"
        )
        row = QHBoxLayout(frame)
        row.setContentsMargins(10, 6, 10, 6)
        row.setSpacing(8)

        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"color:{COLORS['muted']};font-size:11px;min-width:80px;"
            f"border:none;background:transparent;"
        )
        row.addWidget(lbl)

        item_lbl = QLabel(inv_entry["name"] if inv_entry else "— Leer —")
        col = COLORS["text"] if inv_entry else COLORS["muted"]
        item_lbl.setStyleSheet(
            f"color:{col};font-size:13px;border:none;background:transparent;"
        )
        row.addWidget(item_lbl, 1)

        if inv_entry:
            btn = QPushButton("Ablegen")
            btn.setObjectName("secondary-btn")
            btn.setFixedWidth(80)
            btn.clicked.connect(unequip_fn)
        else:
            btn = QPushButton("Ausrüsten")
            btn.setObjectName("primary-btn")
            btn.setFixedWidth(90)
            btn.clicked.connect(equip_fn)
        row.addWidget(btn)

        return frame

    def _build_weapon_set_box(self, set_idx: int) -> QGroupBox:
        eq = self._data.get("equipment", {})
        active = eq.get("active_weapon_set", 0)
        ws_list = eq.get("weapon_sets", [
            {"main_hand": None, "off_hand": None},
            {"main_hand": None, "off_hand": None},
        ])
        ws = ws_list[set_idx] if set_idx < len(ws_list) else {}

        grp = QGroupBox(f"Waffenset {set_idx + 1}")
        if set_idx == active:
            grp.setStyleSheet(
                f"QGroupBox{{border:2px solid {COLORS['gold']};border-radius:6px;"
                f"margin-top:14px;padding:4px;}}"
                f"QGroupBox::title{{color:{COLORS['gold']};"
                f"subcontrol-origin:margin;left:8px;padding:0 4px;}}"
            )
        vlay = QVBoxLayout(grp)
        vlay.setSpacing(6)

        if set_idx != active:
            btn_sw = QPushButton(f"Zu Waffenset {set_idx + 1} wechseln")
            btn_sw.setObjectName("primary-btn")
            btn_sw.clicked.connect(lambda si=set_idx: self._on_switch_weapon_set(si))
            vlay.addWidget(btn_sw)
        else:
            lbl_act = QLabel("● Aktives Set")
            lbl_act.setStyleSheet(
                f"color:{COLORS['gold']};font-size:11px;border:none;background:transparent;"
            )
            vlay.addWidget(lbl_act)

        main_entry = ws.get("main_hand")
        off_entry  = ws.get("off_hand")

        vlay.addWidget(self._build_slot_frame(
            "Haupthand", main_entry,
            equip_fn=lambda si=set_idx: self._on_equip_weapon(si, "main_hand"),
            unequip_fn=lambda si=set_idx: self._on_unequip_weapon(si, "main_hand"),
        ))
        vlay.addWidget(self._build_slot_frame(
            "Nebenhand", off_entry,
            equip_fn=lambda si=set_idx: self._on_equip_weapon(si, "off_hand"),
            unequip_fn=lambda si=set_idx: self._on_unequip_weapon(si, "off_hand"),
        ))
        return grp

    def _build_armor_box(self) -> QGroupBox:
        eq = self._data.get("equipment", {})
        armor_entry = eq.get("armor_slot")
        grp = QGroupBox("Rüstung")
        vlay = QVBoxLayout(grp)
        vlay.setSpacing(6)
        vlay.addWidget(self._build_slot_frame(
            "Rüstung", armor_entry,
            equip_fn=self._on_equip_armor,
            unequip_fn=self._on_unequip_armor,
        ))
        return grp

    def _build_attunement_box(self) -> QGroupBox:
        eq = self._data.get("equipment", {})
        slots = eq.get("attunement_slots", [None, None, None])
        grp = QGroupBox("Einstimmung (max. 3)")
        vlay = QVBoxLayout(grp)
        vlay.setSpacing(6)
        for i, entry in enumerate(slots[:3]):
            vlay.addWidget(self._build_slot_frame(
                f"Slot {i + 1}", entry,
                equip_fn=lambda si=i: self._on_equip_attunement(si),
                unequip_fn=lambda si=i: self._on_unequip_attunement(si),
            ))
        return grp

    def _build_equipment_tab(self) -> QWidget:
        self._ensure_equipment_fields()
        w = QWidget()
        outer = QVBoxLayout(w)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        sets_row = QHBoxLayout()
        sets_row.setSpacing(12)
        sets_row.addWidget(self._build_weapon_set_box(0))
        sets_row.addWidget(self._build_weapon_set_box(1))
        layout.addLayout(sets_row)

        layout.addWidget(self._build_armor_box())
        layout.addWidget(self._build_attunement_box())
        layout.addStretch()

        scroll.setWidget(container)
        outer.addWidget(scroll, 1)
        return w

    def _on_switch_weapon_set(self, set_idx: int) -> None:
        self._ensure_equipment_fields()
        self._data["equipment"]["active_weapon_set"] = set_idx
        self._sync_legacy_eq()
        cur = self.tabs.currentIndex()
        self._rebuild_tabs()
        self.tabs.setCurrentIndex(cur)

    def _on_equip_weapon(self, set_idx: int, slot: str) -> None:
        inv = self._data.get("inventory", [])
        if slot == "off_hand":
            candidates = [
                e for e in inv
                if e.get("item_type") == "weapon"
                or (e.get("item_type") == "armor"
                    and (ItemService.get_armor_raw(e.get("item_index", "")) or {}).get("category") == "shield")
            ]
        else:
            candidates = [e for e in inv if e.get("item_type") == "weapon"]

        if not candidates:
            QMessageBox.information(self, "Inventar leer",
                "Keine geeigneten Gegenstände im Inventar.")
            return

        from src.client.gui.dialogs.inventory_dialog import EquipSlotDialog
        dlg = EquipSlotDialog(candidates, parent=self)
        if not dlg.exec():
            return

        self._ensure_equipment_fields()
        self._data["equipment"]["weapon_sets"][set_idx][slot] = dlg.selected_entry
        self._sync_legacy_eq()
        cur = self.tabs.currentIndex()
        self._rebuild_tabs()
        self.tabs.setCurrentIndex(cur)

    def _on_unequip_weapon(self, set_idx: int, slot: str) -> None:
        self._ensure_equipment_fields()
        self._data["equipment"]["weapon_sets"][set_idx][slot] = None
        self._sync_legacy_eq()
        cur = self.tabs.currentIndex()
        self._rebuild_tabs()
        self.tabs.setCurrentIndex(cur)

    def _on_equip_armor(self) -> None:
        inv = self._data.get("inventory", [])
        candidates = [
            e for e in inv
            if e.get("item_type") == "armor"
            and (ItemService.get_armor_raw(e.get("item_index", "")) or {}).get("category") != "shield"
        ]
        if not candidates:
            QMessageBox.information(self, "Inventar leer",
                "Keine Rüstungen im Inventar.")
            return

        from src.client.gui.dialogs.inventory_dialog import EquipSlotDialog
        dlg = EquipSlotDialog(candidates, parent=self)
        if not dlg.exec():
            return

        self._ensure_equipment_fields()
        self._data["equipment"]["armor_slot"] = dlg.selected_entry
        self._sync_legacy_eq()
        cur = self.tabs.currentIndex()
        self._rebuild_tabs()
        self.tabs.setCurrentIndex(cur)

    def _on_unequip_armor(self) -> None:
        self._ensure_equipment_fields()
        self._data["equipment"]["armor_slot"] = None
        self._sync_legacy_eq()
        cur = self.tabs.currentIndex()
        self._rebuild_tabs()
        self.tabs.setCurrentIndex(cur)

    def _on_equip_attunement(self, slot_idx: int) -> None:
        inv = self._data.get("inventory", [])
        candidates = [
            e for e in inv
            if e.get("item_type") == "magic-item"
            and (ItemService.get_magic_item_raw(e.get("item_index", "")) or {}).get("attunement")
        ]
        if not candidates:
            QMessageBox.information(self, "Inventar leer",
                "Keine einstimmbaren Gegenstände im Inventar.")
            return

        from src.client.gui.dialogs.inventory_dialog import EquipSlotDialog
        dlg = EquipSlotDialog(candidates, parent=self)
        if not dlg.exec():
            return

        self._ensure_equipment_fields()
        self._data["equipment"]["attunement_slots"][slot_idx] = dlg.selected_entry
        cur = self.tabs.currentIndex()
        self._rebuild_tabs()
        self.tabs.setCurrentIndex(cur)

    def _on_unequip_attunement(self, slot_idx: int) -> None:
        self._ensure_equipment_fields()
        self._data["equipment"]["attunement_slots"][slot_idx] = None
        cur = self.tabs.currentIndex()
        self._rebuild_tabs()
        self.tabs.setCurrentIndex(cur)

    # ── Save ──────────────────────────────────────────────────────────────

    def _save(self):
        data = dict(self._data)
        data["hp"] = {
            "max": self.hp_max.value(),
            "current": self.hp_current.value(),
            "temp": self.hp_temp.value(),
        }
        data["death_saves"] = {
            "successes": sum(cb.isChecked() for cb in self.death_success_cbs),
            "failures": sum(cb.isChecked() for cb in self.death_fail_cbs),
        }
        data["equipment"] = data.get("equipment", {})
        data["equipment"]["currency"] = {k: sp.value() for k, sp in self.currency_spins.items()}
        data["traits"] = {k: te.toPlainText() for k, te in self.trait_edits.items()}
        data["notes"] = self.notes_edit.toPlainText()

        try:
            r = requests.put(
                f"{self.base_url}/api/characters/{self.char['id']}",
                json={"name": self.char["name"], "data": data},
                headers={"Authorization": f"Bearer {self.auth_token}"},
                timeout=5,
            )
            if r.status_code == 200:
                self._data = data
                self.status_lbl.setText("Gespeichert ✓")
                self.status_lbl.setStyleSheet(f"color:{COLORS['success']};font-size:12px;")
            else:
                self.status_lbl.setText(r.json().get("error", "Fehler beim Speichern."))
                self.status_lbl.setStyleSheet(f"color:{COLORS['error']};font-size:12px;")
        except Exception as e:
            self.status_lbl.setText(str(e))
            self.status_lbl.setStyleSheet(f"color:{COLORS['error']};font-size:12px;")
