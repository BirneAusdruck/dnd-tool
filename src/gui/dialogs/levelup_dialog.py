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
from PySide6.QtCore import Qt

from src.gui.theme import COLORS
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

    def __init__(self, char_data: dict, parent=None):
        super().__init__(parent)
        self._info = get_level_up_info(char_data)
        self._char_data = char_data
        self._roll_value: int | None = None

        # Public results
        self.hp_gain: int = self._info["hp_average"]
        self.asi_changes: dict[str, int] | None = None
        self.feat_index: str | None = None

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

        title = QLabel(
            f"Level {info['current_level']} → Level {info['new_level']}  |  {cls_name}"
        )
        title.setStyleSheet(
            f"font-size:18px;font-weight:bold;color:{COLORS['text']};"
        )
        root.addWidget(title)

        # Scrollable body
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setSpacing(12)

        # New features
        if info["new_features"]:
            feat_grp = QGroupBox(f"Neue Fähigkeiten (Level {info['new_level']})")
            feat_inner = QVBoxLayout(feat_grp)
            for f in info["new_features"]:
                lbl = QLabel(f"• {f}")
                lbl.setWordWrap(True)
                lbl.setStyleSheet(f"color:{COLORS['subtext']};font-size:13px;")
                feat_inner.addWidget(lbl)
            layout.addWidget(feat_grp)

        # HP gain
        layout.addWidget(self._build_hp_section())

        # ASI or Feat (if applicable)
        self._asi_spins: dict[str, QSpinBox] = {}
        self._asi_total_lbl: QLabel | None = None
        self._feat_list: QListWidget | None = None
        self._feat_detail: QTextEdit | None = None
        self._asi_feat_stack: QStackedWidget | None = None
        if info["is_asi"]:
            layout.addWidget(self._build_asi_feat_section())

        # Spell slot changes
        sp_info = info.get("spell_info")
        if sp_info and sp_info["old_slots"] != sp_info["new_slots"]:
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
        grp = QGroupBox("Zauberplätze")
        grid = QGridLayout(grp)
        old_s, new_s = sp_info["old_slots"], sp_info["new_slots"]
        for i in range(max(len(old_s), len(new_s))):
            old = old_s[i] if i < len(old_s) else 0
            new = new_s[i] if i < len(new_s) else 0
            grid.addWidget(QLabel(f"Grad {i+1}:"), 0, i)
            color = COLORS["success"] if new > old else COLORS["text"]
            lbl = QLabel(f"{old} → {new}")
            lbl.setStyleSheet(f"color:{color};font-weight:bold;")
            grid.addWidget(lbl, 1, i)
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

        title = QLabel(
            f"Level senken: {info['current_level']} → {info['new_level']}  |  {cls_name}"
        )
        title.setStyleSheet(
            f"font-size:16px;font-weight:bold;color:{COLORS['error']};"
        )
        root.addWidget(title)

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
