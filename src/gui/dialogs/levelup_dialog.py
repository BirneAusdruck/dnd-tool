"""
LevelUpDialog  – shown when the user wants to gain a level.
LevelDownDialog – confirmation + summary shown before removing a level.
"""

from __future__ import annotations
import random

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QGridLayout, QSpinBox, QRadioButton, QScrollArea,
    QFrame, QWidget, QButtonGroup, QListWidget, QListWidgetItem,
    QTextEdit, QStackedWidget, QSplitter,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

from src.gui.theme import COLORS
from src.gui import assets
from src.game import srd_loader as srd
from src.game.level_manager import (
    get_level_up_info, get_level_down_info, get_asi_levels, get_new_features,
)

def _section(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(f"font-size:14px;font-weight:bold;color:{COLORS['accent']};")
    return lbl


def _muted(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(f"color:{COLORS['muted']};font-size:12px;")
    lbl.setWordWrap(True)
    return lbl

# ── LevelUpDialog ──────────────────────────────────────────────────────────

class LevelUpDialog(QDialog):
    """
    Collects the user's level-up choices (HP method, ASI).
    After .exec() returns Accepted, read .hp_gain and .asi_changes.
    """

    def __init__(self, char_data: dict, class_index: str | None, parent=None):
        super().__init__(parent)
        self._info = get_level_up_info(char_data, class_index)
        self._char_data = char_data
        self._roll_value: int | None = None

        # Public results
        self.hp_gain: int = self._info["hp_average"]
        self.asi_changes: dict[str, int] | None = None
        self.feat_index: str | None = None
        self.subclass_index: str | None = None

        cls_name = (srd.get_class(self._info["class_index"]) or {}).get(
            "name", self._info["class_index"]
        )
        self.setWindowTitle(f"Level Up → Level {self._info['new_level']}")
        self.setMinimumSize(640, 560)
        self._build_ui(cls_name)

    # ── Build ──────────────────────────────────────────────────────────────

    def _build_ui(self, cls_name: str) -> None:
        info = self._info
        root = QVBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(20, 16, 20, 16)

        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        cls_icon_p = assets.ICONS_CLASS.get(self._info["class_index"])
        if cls_icon_p:
            ic_lbl = QLabel()
            ic_lbl.setPixmap(QIcon(assets.resolve(cls_icon_p)).pixmap(36, 36))
            ic_lbl.setStyleSheet("background:transparent;")
            title_row.addWidget(ic_lbl)
        title = QLabel(
            f"Level {info['current_level']} → Level {info['new_level']}  |  {cls_name}"
        )
        title.setStyleSheet(f"font-size:18px;font-weight:bold;color:{COLORS['text']};")
        title_row.addWidget(title)
        title_row.addStretch()
        root.addLayout(title_row)

        # Scrollable body
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setSpacing(12)

        # New features
        if info["new_features"]:
            feat_grp = QGroupBox(f"Neue Fähigkeiten ({cls_name} Level {info['new_class_level']})")
            feat_inner = QVBoxLayout(feat_grp)
            for f in info["new_features"]:
                lbl = QLabel(f"• {f}")
                lbl.setWordWrap(True)
                lbl.setStyleSheet(f"color:{COLORS['subtext']};font-size:13px;")
                feat_inner.addWidget(lbl)
            layout.addWidget(feat_grp)

        # HP gain
        layout.addWidget(self._build_hp_section())

        # Subclass selection (if applicable)
        self._subclass_bg: QButtonGroup | None = None
        if info["is_subclass"]:
            layout.addWidget(self._build_subclass_section())

        # ASI or Feat (if applicable)
        self._asi_spins: dict[str, QSpinBox] = {}
        self._asi_total_lbl: QLabel | None = None
        self._feat_list: QListWidget | None = None
        self._feat_detail: QTextEdit | None = None
        self._asi_feat_stack: QStackedWidget | None = None
        if info["is_asi"]:
            layout.addWidget(self._build_asi_feat_section())

        # Spell slot changes (combined, per-class, or pact)
        sp_info = info.get("spell_info")
        if sp_info and (
            sp_info["old_slots"] != sp_info["new_slots"]
            or sp_info.get("old_pact") != sp_info.get("new_pact")
        ):
            layout.addWidget(self._build_spell_section(sp_info))

        layout.addStretch()
        scroll.setWidget(inner)
        root.addWidget(scroll, 1)

        # Footer
        btn_row = QHBoxLayout()
        self.error_lbl = QLabel("")
        self.error_lbl.setStyleSheet(f"color:{COLORS['error']};font-size:12px;")
        btn_cancel = QPushButton("Abbrechen")
        btn_cancel.setObjectName("secondary-btn")
        btn_cancel.clicked.connect(self.reject)
        btn_ok = QPushButton("Level Up bestätigen ✓")
        btn_ok.setObjectName("primary-btn")
        btn_ok.clicked.connect(self._on_accept)
        btn_row.addWidget(self.error_lbl, 1)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        root.addLayout(btn_row)

    def _build_hp_section(self) -> QGroupBox:
        info = self._info
        hit_die = info["hit_die"]
        con_mod = info["con_mod"]
        avg = info["hp_average"]

        grp = QGroupBox("Trefferpunkte")
        hp_grid = QGridLayout(grp)

        info_lbl = QLabel(
            f"Trefferwürfel: d{hit_die}    KON-Mod: {con_mod:+d}    Durchschnitt: {avg}"
        )
        hp_grid.addWidget(info_lbl, 0, 0, 1, 3)

        self.rb_avg = QRadioButton(f"Durchschnitt nehmen ({avg} HP)")
        self.rb_roll = QRadioButton(f"Würfeln (d{hit_die}{con_mod:+d})")
        self.rb_manual = QRadioButton("Manuell eingeben:")
        self.rb_avg.setChecked(True)

        bg = QButtonGroup(self)
        for rb in (self.rb_avg, self.rb_roll, self.rb_manual):
            bg.addButton(rb)

        self.roll_result_lbl = QLabel("—")
        self.roll_result_lbl.setStyleSheet(
            f"color:{COLORS['gold']};font-weight:bold;font-size:15px;"
        )
        btn_roll = QPushButton("Würfeln")
        btn_roll.setObjectName("secondary-btn")
        die_icon_p = assets.ICONS_DICE.get(f"d{hit_die}")
        if die_icon_p:
            btn_roll.setIcon(QIcon(assets.resolve(die_icon_p)))
        btn_roll.clicked.connect(self._do_hp_roll)

        self.manual_spin = QSpinBox()
        self.manual_spin.setRange(max(1, 1 + con_mod), hit_die + max(0, con_mod))
        self.manual_spin.setValue(avg)

        hp_grid.addWidget(self.rb_avg, 1, 0, 1, 3)
        hp_grid.addWidget(self.rb_roll, 2, 0)
        hp_grid.addWidget(btn_roll, 2, 1)
        hp_grid.addWidget(self.roll_result_lbl, 2, 2)
        hp_grid.addWidget(self.rb_manual, 3, 0)
        hp_grid.addWidget(self.manual_spin, 3, 1)
        return grp

    def _build_subclass_section(self) -> QGroupBox:
        info = self._info
        grp = QGroupBox(f"{info['subclass_name']} wählen")
        layout = QVBoxLayout(grp)
        layout.addWidget(_muted(
            f"Du erreichst {info['class_index'].capitalize()} Level {info['new_class_level']} "
            f"und wählst jetzt eine {info['subclass_name']}."
        ))
        self._subclass_bg = QButtonGroup(self)
        for choice in info["subclass_choices"]:
            rb = QRadioButton(choice)
            self._subclass_bg.addButton(rb)
            layout.addWidget(rb)
        buttons = self._subclass_bg.buttons()
        if buttons:
            buttons[0].setChecked(True)
        return grp

    def _build_asi_feat_section(self) -> QGroupBox:
        grp = QGroupBox("Attributsteigerung (ASI) oder Talent (Feat)")
        outer = QVBoxLayout(grp)

        # Toggle row
        toggle_row = QHBoxLayout()
        self._rb_asi = QRadioButton("Attributsteigerung (ASI)")
        self._rb_feat = QRadioButton("Talent (Feat)")
        self._rb_asi.setChecked(True)
        bg = QButtonGroup(self)
        bg.addButton(self._rb_asi)
        bg.addButton(self._rb_feat)
        self._rb_asi.toggled.connect(self._on_asi_feat_toggle)
        toggle_row.addWidget(self._rb_asi)
        toggle_row.addWidget(self._rb_feat)
        toggle_row.addStretch()
        outer.addLayout(toggle_row)

        # Stacked: page 0 = ASI, page 1 = Feat
        self._asi_feat_stack = QStackedWidget()

        # Page 0: ASI
        asi_page = QWidget()
        asi_layout = QVBoxLayout(asi_page)
        asi_layout.setContentsMargins(0, 4, 0, 0)
        asi_layout.addWidget(_muted(
            "+2 auf ein Attribut ODER +1/+1 auf zwei verschiedene. "
            "Kein Attribut darf 20 überschreiten."
        ))
        scores = self._info["current_scores"]
        grid = QGridLayout()
        for i, ab in enumerate(srd.ABILITIES):
            current_val = scores.get(ab, 10)
            max_add = min(2, 20 - current_val)
            grid.addWidget(QLabel(f"{ab}  (aktuell {current_val}):"), i, 0)
            sp = QSpinBox()
            sp.setRange(0, max_add)
            sp.setValue(0)
            sp.valueChanged.connect(self._on_asi_changed)
            self._asi_spins[ab] = sp
            grid.addWidget(sp, i, 1)
        asi_layout.addLayout(grid)
        self._asi_total_lbl = QLabel("Verteilt: 0 / 2")
        self._asi_total_lbl.setStyleSheet(f"color:{COLORS['gold']};font-weight:bold;")
        asi_layout.addWidget(self._asi_total_lbl)
        self._asi_feat_stack.addWidget(asi_page)

        # Page 1: Feat list
        feat_page = QWidget()
        feat_layout = QHBoxLayout(feat_page)
        feat_layout.setContentsMargins(0, 4, 0, 0)

        self._feat_list = QListWidget()
        self._feat_list.setMaximumWidth(200)
        for feat in srd.get_feats():
            item = QListWidgetItem(feat["name"])
            item.setData(Qt.ItemDataRole.UserRole, feat["index"])
            # Grey out if already held
            if feat["index"] in self._char_data.get("basics", {}).get("feats", []):
                item.setForeground(Qt.GlobalColor.gray)
                item.setToolTip("Bereits vorhanden")
            self._feat_list.addItem(item)
        self._feat_list.currentItemChanged.connect(self._on_feat_selected)
        feat_layout.addWidget(self._feat_list)

        self._feat_detail = QTextEdit()
        self._feat_detail.setReadOnly(True)
        self._feat_detail.setPlaceholderText("← Talent auswählen für Details")
        feat_layout.addWidget(self._feat_detail, 1)

        self._asi_feat_stack.addWidget(feat_page)
        outer.addWidget(self._asi_feat_stack)
        return grp

    def _on_asi_feat_toggle(self, asi_checked: bool) -> None:
        if self._asi_feat_stack:
            self._asi_feat_stack.setCurrentIndex(0 if asi_checked else 1)

    def _on_feat_selected(self, current: QListWidgetItem, _prev) -> None:
        if not current or not self._feat_detail:
            return
        feat = srd.get_feat(current.data(Qt.ItemDataRole.UserRole))
        if not feat:
            return
        lines = [f"<b>{feat['name']}</b>"]
        if feat.get("prerequisite"):
            lines.append(f"<i>Voraussetzung: {feat['prerequisite']}</i>")
        lines.append("")
        lines.append(feat["desc"])
        lines.append("<ul>")
        for b in feat.get("benefits", []):
            lines.append(f"<li>{b}</li>")
        lines.append("</ul>")
        self._feat_detail.setHtml("<br>".join(lines))

    def _build_spell_section(self, sp_info: dict) -> QGroupBox:
        title = "Kombinierte Zauberplätze" if sp_info.get("is_multiclass") else "Zauberplätze"
        grp = QGroupBox(title)
        outer = QVBoxLayout(grp)

        # Combined / per-class slots
        old_s, new_s = sp_info["old_slots"], sp_info["new_slots"]
        if old_s or new_s:
            grid = QGridLayout()
            for i in range(max(len(old_s), len(new_s))):
                old = old_s[i] if i < len(old_s) else 0
                new = new_s[i] if i < len(new_s) else 0
                grid.addWidget(QLabel(f"Grad {i+1}:"), 0, i)
                color = COLORS["success"] if new > old else COLORS["text"]
                lbl = QLabel(f"{old} → {new}")
                lbl.setStyleSheet(f"color:{color};font-weight:bold;")
                grid.addWidget(lbl, 1, i)
            outer.addLayout(grid)

        # Warlock pact slots (separate)
        old_pact, new_pact = sp_info.get("old_pact", (0, 0)), sp_info.get("new_pact", (0, 0))
        if old_pact != new_pact and (old_pact[0] or new_pact[0]):
            pact_lbl = QLabel(
                f"Pakt-Slots: {old_pact[0]}×Grad {old_pact[1]} → "
                f"{new_pact[0]}×Grad {new_pact[1]}"
            )
            pact_lbl.setStyleSheet(f"color:{COLORS['accent']};font-weight:bold;font-size:12px;")
            outer.addWidget(pact_lbl)

        return grp

    # ── Slots ──────────────────────────────────────────────────────────────

    def _do_hp_roll(self) -> None:
        self.rb_roll.setChecked(True)
        roll = random.randint(1, self._info["hit_die"])
        total = max(1, roll + self._info["con_mod"])
        self._roll_value = total
        self.roll_result_lbl.setText(
            f"{roll} + {self._info['con_mod']:+d} = {total}"
        )

    def _on_asi_changed(self) -> None:
        if not self._asi_total_lbl:
            return
        total = sum(sp.value() for sp in self._asi_spins.values())
        if total == 2:
            color = COLORS["success"]
        elif total > 2:
            color = COLORS["error"]
        else:
            color = COLORS["gold"]
        self._asi_total_lbl.setText(f"Verteilt: {total} / 2")
        self._asi_total_lbl.setStyleSheet(f"color:{color};font-weight:bold;")

    def _on_accept(self) -> None:
        self.error_lbl.setText("")

        # HP
        if self.rb_avg.isChecked():
            self.hp_gain = self._info["hp_average"]
        elif self.rb_roll.isChecked():
            if self._roll_value is None:
                self.error_lbl.setText("Bitte erst würfeln.")
                return
            self.hp_gain = self._roll_value
        else:
            self.hp_gain = self.manual_spin.value()

        # ASI or Feat
        if self._info["is_asi"]:
            feat_chosen = self._rb_feat.isChecked() if hasattr(self, "_rb_feat") else False
            if feat_chosen:
                item = self._feat_list.currentItem() if self._feat_list else None
                if not item:
                    self.error_lbl.setText("Bitte ein Talent aus der Liste auswählen.")
                    return
                self.feat_index = item.data(Qt.ItemDataRole.UserRole)
            else:
                total = sum(sp.value() for sp in self._asi_spins.values())
                if total != 2:
                    self.error_lbl.setText(
                        f"ASI: Bitte genau 2 Punkte verteilen (aktuell: {total})."
                    )
                    return
                scores = self._info["current_scores"]
                for ab, sp in self._asi_spins.items():
                    if sp.value() > 0 and scores.get(ab, 10) + sp.value() > 20:
                        self.error_lbl.setText(f"{ab} würde 20 überschreiten.")
                        return
                self.asi_changes = {
                    ab: sp.value()
                    for ab, sp in self._asi_spins.items()
                    if sp.value() > 0
                }

        # Subclass
        if self._info["is_subclass"]:
            checked = self._subclass_bg.checkedButton() if self._subclass_bg else None
            if not checked:
                self.error_lbl.setText("Bitte eine Unterklasse auswählen.")
                return
            self.subclass_index = checked.text()

        self.accept()


# ── LevelDownDialog ────────────────────────────────────────────────────────

class LevelDownDialog(QDialog):
    """Confirmation dialog summarising what will be undone by a level-down."""

    def __init__(self, char_data: dict, parent=None):
        super().__init__(parent)
        info = get_level_down_info(char_data)
        cls_name = (srd.get_class(info["class_index"]) or {}).get(
            "name", info["class_index"]
        )
        self.setWindowTitle("Level senken")
        self.setMinimumSize(440, 300)

        root = QVBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(20, 16, 20, 16)

        cls_level_info = f" (Stufe {info['class_level']})" if info.get("class_level") else ""
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        dn_icon_p = assets.ICONS_CLASS.get(info["class_index"])
        if dn_icon_p:
            dn_ic = QLabel()
            dn_ic.setPixmap(QIcon(assets.resolve(dn_icon_p)).pixmap(32, 32))
            dn_ic.setStyleSheet("background:transparent;")
            title_row.addWidget(dn_ic)
        title = QLabel(
            f"Level senken: {info['current_level']} → {info['new_level']}  |  {cls_name}{cls_level_info}"
        )
        title.setStyleSheet(f"font-size:16px;font-weight:bold;color:{COLORS['error']};")
        title_row.addWidget(title)
        title_row.addStretch()
        root.addLayout(title_row)

        grp = QGroupBox("Folgende Änderungen werden rückgängig gemacht:")
        grp_inner = QVBoxLayout(grp)

        hp_note = info["hp_to_remove"]
        grp_inner.addWidget(QLabel(
            f"• HP-Maximum sinkt um {hp_note}" if hp_note else "• HP-Verlust unbekannt (Level ohne Historie)"
        ))

        if info["asi_undone"]:
            changes_str = ", ".join(
                f"{ab} −{v}" for ab, v in info["asi_undone"].items()
            )
            grp_inner.addWidget(QLabel(f"• ASI wird rückgängig gemacht ({changes_str})"))

        if info.get("subclass_undone"):
            grp_inner.addWidget(QLabel(f"• Unterklasse wird entfernt: {info['subclass_undone']}"))

        if info.get("feat_undone"):
            feat_name = (srd.get_feat(info["feat_undone"]) or {}).get("name", info["feat_undone"])
            grp_inner.addWidget(QLabel(f"• Talent wird entfernt: {feat_name}"))

        for feat in info["features_removed"]:
            lbl = QLabel(f"• Fähigkeit entfernt: {feat}")
            lbl.setStyleSheet(f"color:{COLORS['muted']};font-size:12px;")
            grp_inner.addWidget(lbl)

        root.addWidget(grp)
        root.addWidget(_muted(
            "Du kannst jederzeit wieder aufleveln, um die Änderungen rückgängig zu machen."
        ))
        root.addStretch()

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Abbrechen")
        btn_cancel.setObjectName("secondary-btn")
        btn_cancel.clicked.connect(self.reject)
        btn_ok = QPushButton("Level senken ↓")
        btn_ok.setObjectName("primary-btn")
        btn_ok.setStyleSheet(
            f"QPushButton{{background:{COLORS['error']};color:white;"
            f"border-radius:6px;padding:8px 16px;}}"
        )
        btn_ok.clicked.connect(self.accept)
        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        root.addLayout(btn_row)

# ── ClassPickerDialog ─────────────────────────────────────────────────────────

class ClassPickerDialog(QDialog):
    """
    Lets the user choose which class to level up into.
    Already-held classes are highlighted; new classes appear as multiclass options.
    After .exec() returns Accepted, read .selected_class_index.
    """

    def __init__(self, char_data: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Klasse für Level Up wählen")
        self.setMinimumSize(600, 420)
        self.selected_class_index: str | None = None
        self._build_ui(char_data)

    def _build_ui(self, char_data: dict) -> None:
        held = {
            c["class_index"]: c["level"]
            for c in char_data["basics"].get("classes", [])
        }

        root = QVBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(20, 16, 20, 16)

        root.addWidget(_section("Klasse für Level Up wählen"))
        root.addWidget(_muted(
            "Bereits gehaltene Klassen sind hervorgehoben. "
            "Wähle eine neue Klasse für Multiclassing."
        ))

        spl = QSplitter(Qt.Orientation.Horizontal)

        # Left: class list with icons and held-class indicators
        left_w = QWidget()
        left = QVBoxLayout(left_w)
        left.setContentsMargins(0, 0, 0, 0)
        left.addWidget(QLabel("Klasse:"))
        self._class_list = QListWidget()
        for cls in srd.get_classes():
            idx = cls["index"]
            held_lvl = held.get(idx)
            label = cls["name"] + (f"  (Stufe {held_lvl})" if held_lvl else "  [neu]")
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, idx)
            icon_path = assets.ICONS_CLASS.get(idx)
            if icon_path:
                item.setIcon(QIcon(assets.resolve(icon_path)))
            if held_lvl:
                item.setForeground(Qt.GlobalColor.cyan)
            self._class_list.addItem(item)
        self._class_list.currentItemChanged.connect(self._on_class_changed)
        left.addWidget(self._class_list)
        spl.addWidget(left_w)

        # Right: detail area
        right_w = QWidget()
        right = QVBoxLayout(right_w)
        right.setContentsMargins(0, 0, 0, 0)
        right.addWidget(QLabel("Details:"))
        self._detail = QTextEdit()
        self._detail.setReadOnly(True)
        self._detail.setPlaceholderText("← Klasse auswählen")
        right.addWidget(self._detail)
        spl.addWidget(right_w)

        spl.setStretchFactor(0, 1)
        spl.setStretchFactor(1, 2)
        root.addWidget(spl, 1)

        # Footer
        btn_row = QHBoxLayout()
        self._error_lbl = QLabel("")
        self._error_lbl.setStyleSheet(f"color:{COLORS['error']};font-size:12px;")
        btn_cancel = QPushButton("Abbrechen")
        btn_cancel.setObjectName("secondary-btn")
        btn_cancel.clicked.connect(self.reject)
        self._btn_ok = QPushButton("Klasse wählen →")
        self._btn_ok.setObjectName("primary-btn")
        self._btn_ok.setEnabled(False)
        self._btn_ok.clicked.connect(self._on_accept)
        btn_row.addWidget(self._error_lbl, 1)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(self._btn_ok)
        root.addLayout(btn_row)

    def _on_class_changed(self, current: QListWidgetItem, _) -> None:
        if not current:
            self._btn_ok.setEnabled(False)
            return
        self._btn_ok.setEnabled(True)
        cls = srd.get_class(current.data(Qt.ItemDataRole.UserRole))
        if not cls:
            return
        lines = [cls["name"], "=" * 40]
        lines.append(f"Trefferwürfel: d{cls['hit_die']}")
        lines.append(f"Primärattribute: {', '.join(cls['primary_abilities'])}")
        lines.append(f"Rettungswürfe: {', '.join(cls['saving_throws'])}")
        lines.append(f"Rüstungen: {', '.join(cls['armor_proficiencies']) or '–'}")
        lines.append(f"Waffen: {', '.join(cls['weapon_proficiencies'])}")
        sc = cls["skill_choices"]
        from_str = ", ".join(sc["from"]) if sc["from"] != "any" else "beliebig"
        lines.append(f"Fertigkeiten: {sc['count']} aus ({from_str})")
        if cls.get("spellcasting"):
            sp = cls["spellcasting"]
            lines.append(f"Zauberkunst: {sp['ability']} ({sp['type']})")
        lines.append("")
        lines.append("Level-1-Fähigkeiten:")
        for f in cls["features"].get("1", []):
            lines.append(f"  • {f}")
        self._detail.setPlainText("\n".join(lines))

    def _on_accept(self) -> None:
        item = self._class_list.currentItem()
        if not item:
            self._error_lbl.setText("Bitte eine Klasse auswählen.")
            return
        self.selected_class_index = item.data(Qt.ItemDataRole.UserRole)
        self.accept()
