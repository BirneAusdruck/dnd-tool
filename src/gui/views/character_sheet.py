"""
Full character sheet view — read/edit mode.
Organized like the official DnD character sheet.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QSpinBox, QGroupBox, QScrollArea, QFrame,
    QPushButton, QTabWidget, QTextEdit, QCheckBox, QMessageBox,
    QSizePolicy,
)
from PySide6.QtCore import Qt

import requests

from src.gui.theme import COLORS
from src.game.character_builder import derive_sheet_values, proficiency_bonus
from src.game import srd_loader as srd


def _fmt_mod(val: int) -> str:
    return f"+{val}" if val >= 0 else str(val)


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
    def __init__(self, ability: str, score: int, parent=None):
        super().__init__(parent)
        self.ability = ability
        self.setFixedWidth(80)
        layout = QVBoxLayout(self)
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

        layout.addWidget(ab_lbl)
        layout.addWidget(self.mod_lbl)
        layout.addWidget(self.score_lbl)


# ── Skill Row ──────────────────────────────────────────────────────────────

class _SkillRow(QWidget):
    def __init__(self, skill_name: str, ability: str, bonus: int, proficient: bool, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 1, 4, 1)
        layout.setSpacing(6)

        dot = QLabel("●" if proficient else "○")
        dot.setFixedWidth(14)
        col = COLORS["success"] if proficient else COLORS["muted"]
        dot.setStyleSheet(f"color:{col};font-size:10px;background:transparent;")

        bonus_lbl = QLabel(_fmt_mod(bonus))
        bonus_lbl.setFixedWidth(36)
        b_col = COLORS["text"] if proficient else COLORS["subtext"]
        bonus_lbl.setStyleSheet(f"color:{b_col};font-weight:{'bold' if proficient else 'normal'};background:transparent;")

        name_lbl = QLabel(f"{skill_name}")
        name_lbl.setStyleSheet(f"color:{COLORS['subtext']};font-size:12px;background:transparent;")

        ab_lbl = QLabel(f"({ability})")
        ab_lbl.setStyleSheet(f"color:{COLORS['muted']};font-size:11px;background:transparent;")
        ab_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

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
        self._derived = derive_sheet_values(self._data) if self._data.get("ability_scores") else {}

        basics = self._data.get("basics", {})
        self.setWindowTitle(f"Charakterbogen – {char.get('name', '?')}")
        self.setMinimumSize(1050, 720)
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
        race_name = (srd.get_race(basics.get("race", "")) or {}).get("name", basics.get("race", "?"))
        cls_name = (srd.get_class(basics.get("class", "")) or {}).get("name", basics.get("class", "?"))
        bg_name = (srd.get_background(basics.get("background", "")) or {}).get("name", basics.get("background", "?"))

        name_lbl = QLabel(self.char.get("name", "?"))
        name_lbl.setStyleSheet(f"color:{COLORS['text']};font-size:20px;font-weight:bold;")
        sub_lbl = QLabel(
            f"Level {basics.get('level', 1)}  {race_name}  {cls_name}  •  {bg_name}  •  {basics.get('alignment', '?')}"
        )
        sub_lbl.setStyleSheet(f"color:{COLORS['subtext']};font-size:13px;")

        info_col = QVBoxLayout()
        info_col.addWidget(name_lbl)
        info_col.addWidget(sub_lbl)
        h_layout.addLayout(info_col, 1)

        prof_lbl = QLabel(f"Profizienzbonus: {_fmt_mod(self._derived.get('proficiency_bonus', 2))}")
        prof_lbl.setStyleSheet(f"color:{COLORS['gold']};font-weight:bold;font-size:13px;")
        h_layout.addWidget(prof_lbl)

        root.addWidget(header)

        # ── Tab widget ──
        tabs = QTabWidget()
        tabs.addTab(self._build_main_tab(), "Hauptblatt")
        tabs.addTab(self._build_combat_tab(), "Kampf & HP")
        tabs.addTab(self._build_spells_tab(), "Zauber")
        tabs.addTab(self._build_features_tab(), "Merkmale")
        tabs.addTab(self._build_traits_tab(), "Persönlichkeit")
        root.addWidget(tabs, 1)

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
        ab_inner = QVBoxLayout(ab_grp)
        ab_inner.setSpacing(6)
        for ab in srd.ABILITIES:
            block = _AbilityBlock(ab, scores.get(ab, 10))
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
        for ab in srd.ABILITIES:
            val = derived.get("saving_throws", {}).get(ab, 0)
            proficient = ab in profs.get("saving_throws", [])
            row = _SkillRow(ab, ab, val, proficient)
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

        skill_hdr = QLabel("Fertigkeiten")
        skill_hdr.setStyleSheet(f"color:{COLORS['subtext']};font-size:13px;font-weight:bold;border:none;")
        skill_layout.addWidget(skill_hdr)

        for skill in srd.SKILLS:
            val = derived.get("skills", {}).get(skill["name"], 0)
            proficient = skill["name"] in profs.get("skills", [])
            row = _SkillRow(skill["name"], skill["ability"], val, proficient)
            skill_layout.addWidget(row)
        skill_layout.addStretch()

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

        for col, (lbl_txt, key) in enumerate([
            ("Maximum", "max"), ("Aktuell", "current"), ("Temporär", "temp")
        ]):
            hp_grid.addWidget(_header_label(lbl_txt), 0, col)
            sp = QSpinBox()
            sp.setRange(0, 999)
            sp.setValue(hp.get(key, 0))
            sp.setStyleSheet(f"font-size:18px;color:{COLORS['text']};background:{COLORS['bg']};border:1px solid {COLORS['border']};border-radius:4px;")
            setattr(self, f"hp_{key}", sp)
            hp_grid.addWidget(sp, 1, col)
        layout.addWidget(hp_grp)

        # Combat stats row
        combat_grp = QGroupBox("Kampfwerte")
        combat_grid = QGridLayout(combat_grp)
        combat_grid.setSpacing(12)

        derived = self._derived
        basics = self._data.get("basics", {})

        stats = [
            ("RK", "—"),
            ("Initiative", _fmt_mod(derived.get("initiative", 0))),
            ("Geschwindigkeit", "30 ft"),
            ("Trefferwürfel", self._data.get("hit_dice", {}).get("total", "1d8")),
        ]
        for col, (lbl, val) in enumerate(stats):
            combat_grid.addWidget(_header_label(lbl), 0, col)
            combat_grid.addWidget(_value_label(val, size=18, color=COLORS["gold"]), 1, col)
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
        cls = srd.get_class(basics.get("class", ""))
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
        prof = proficiency_bonus(basics.get("level", 1))
        save_dc = 8 + prof + ab_mod
        spell_attack = prof + ab_mod

        info_grp = QGroupBox("Zauber-Info")
        info_inner = QGridLayout(info_grp)
        for col, (lbl, val) in enumerate([
            ("Zauberwirken-Attribut", ab),
            ("Rettungswurf-SG", str(save_dc)),
            ("Zauberangriff", _fmt_mod(spell_attack)),
        ]):
            info_inner.addWidget(_header_label(lbl), 0, col)
            info_inner.addWidget(_value_label(val, size=16, color=COLORS["gold"]), 1, col)
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

        # Spell slots
        slots = srd.get_class_spell_slots(basics.get("class", ""), basics.get("level", 1))
        if slots:
            slots_grp = QGroupBox("Zauberplätze")
            slots_inner = QGridLayout(slots_grp)
            for i, count in enumerate(slots):
                slots_inner.addWidget(_header_label(f"Grad {i+1}"), 0, i)
                slots_inner.addWidget(_value_label(str(count), size=14), 1, i)
            layout.addWidget(slots_grp)

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
        features = srd.get_class_features(class_idx, level)

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

        # Racial traits
        race_idx = basics.get("race", "")
        subrace_idx = basics.get("subrace")
        race = srd.get_race(race_idx)
        if race:
            race_grp = QGroupBox(f"Volksmerkmale – {race['name']}")
            race_inner = QVBoxLayout(race_grp)
            traits = list(race.get("traits", []))
            if subrace_idx:
                sr = srd.get_subrace(race_idx, subrace_idx)
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
