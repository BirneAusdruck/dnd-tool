"""
Dice roller panel — quick dice buttons, modifier, custom expression.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QSpinBox,
    QCheckBox, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal

from src.client.gui.theme import COLORS


_QUICK_DICE = ["d4", "d6", "d8", "d10", "d12", "d20", "d100"]


class DicePanel(QWidget):
    """Dice roller UI. Emits roll_requested(expr, is_private)."""

    roll_requested = Signal(str, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        # Header
        header = QLabel("🎲 Würfel")
        header.setStyleSheet(
            f"color:{COLORS['accent']};font-weight:bold;font-size:14px;"
        )
        layout.addWidget(header)

        layout.addWidget(self._separator())

        # Quick dice grid
        layout.addWidget(self._section("Schnellwürfel"))
        grid = QGridLayout()
        grid.setSpacing(5)
        for i, die in enumerate(_QUICK_DICE):
            btn = self._die_btn(die)
            btn.clicked.connect(lambda _, d=die: self._quick_roll(d))
            grid.addWidget(btn, i // 4, i % 4)
        layout.addLayout(grid)

        # Count + modifier row
        layout.addWidget(self._section("Anzahl & Modifikator"))
        cm_row = QHBoxLayout()
        cm_row.setSpacing(6)

        lbl_count = QLabel("Anz.:")
        lbl_count.setStyleSheet(f"color:{COLORS['muted']};font-size:11px;")
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 20)
        self.count_spin.setValue(1)
        self.count_spin.setFixedWidth(52)
        self.count_spin.setStyleSheet(self._spin_style())

        lbl_mod = QLabel("Mod:")
        lbl_mod.setStyleSheet(f"color:{COLORS['muted']};font-size:11px;")
        self.mod_spin = QSpinBox()
        self.mod_spin.setRange(-20, 20)
        self.mod_spin.setValue(0)
        self.mod_spin.setFixedWidth(60)
        self.mod_spin.setStyleSheet(self._spin_style())

        cm_row.addWidget(lbl_count)
        cm_row.addWidget(self.count_spin)
        cm_row.addSpacing(8)
        cm_row.addWidget(lbl_mod)
        cm_row.addWidget(self.mod_spin)
        cm_row.addStretch()
        layout.addLayout(cm_row)

        # Advantage / disadvantage
        adv_row = QHBoxLayout()
        adv_row.setSpacing(6)
        btn_adv = self._adv_btn("Vorteil", "#2ecc71")
        btn_dis = self._adv_btn("Nachteil", "#e74c3c")
        btn_adv.clicked.connect(lambda: self._emit("adv"))
        btn_dis.clicked.connect(lambda: self._emit("dis"))
        adv_row.addWidget(btn_adv)
        adv_row.addWidget(btn_dis)
        layout.addLayout(adv_row)

        layout.addWidget(self._separator())

        # Custom expression
        layout.addWidget(self._section("Freier Ausdruck"))
        self.expr_edit = QLineEdit()
        self.expr_edit.setPlaceholderText("z. B.  4d6kh3  /  2d8+5")
        self.expr_edit.setStyleSheet(
            f"background:{COLORS['surface']};color:{COLORS['text']};"
            f"border:1px solid {COLORS['border']};border-radius:4px;"
            f"padding:4px 6px;font-size:12px;"
        )
        self.expr_edit.returnPressed.connect(self._roll_custom)
        layout.addWidget(self.expr_edit)

        # Private checkbox + Roll button
        bottom_row = QHBoxLayout()
        self.private_cb = QCheckBox("Geheimer Wurf")
        self.private_cb.setStyleSheet(f"color:{COLORS['muted']};font-size:11px;")

        btn_roll = QPushButton("Würfeln!")
        btn_roll.setObjectName("primary-btn")
        btn_roll.setFixedHeight(34)
        btn_roll.clicked.connect(self._roll_custom)

        bottom_row.addWidget(self.private_cb)
        bottom_row.addStretch()
        bottom_row.addWidget(btn_roll)
        layout.addLayout(bottom_row)

        layout.addStretch()

        # Recent local history label
        self._last_lbl = QLabel("")
        self._last_lbl.setWordWrap(True)
        self._last_lbl.setStyleSheet(
            f"color:{COLORS['muted']};font-size:11px;"
            f"background:{COLORS['surface']};border-radius:4px;padding:4px 6px;"
        )
        self._last_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._last_lbl)

    # ── Helpers ───────────────────────────────────────────────────────────

    def _die_btn(self, label: str) -> QPushButton:
        btn = QPushButton(label.upper())
        btn.setFixedSize(54, 36)
        btn.setStyleSheet(
            f"QPushButton{{background:{COLORS['surface']};color:{COLORS['gold']};"
            f"border:1px solid {COLORS['border']};border-radius:4px;"
            f"font-weight:bold;font-size:11px;}}"
            f"QPushButton:hover{{background:{COLORS['overlay']};color:white;}}"
            f"QPushButton:pressed{{background:{COLORS['accent']};}}"
        )
        return btn

    def _adv_btn(self, label: str, color: str) -> QPushButton:
        btn = QPushButton(label)
        btn.setStyleSheet(
            f"QPushButton{{background:{color}22;color:{color};"
            f"border:1px solid {color};border-radius:4px;"
            f"font-size:11px;font-weight:bold;padding:4px 8px;}}"
            f"QPushButton:hover{{background:{color}44;}}"
        )
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.setFixedHeight(30)
        return btn

    def _spin_style(self) -> str:
        return (
            f"background:{COLORS['surface']};color:{COLORS['text']};"
            f"border:1px solid {COLORS['border']};border-radius:4px;"
            f"font-size:12px;"
        )

    def _section(self, title: str) -> QLabel:
        lbl = QLabel(title)
        lbl.setStyleSheet(
            f"color:{COLORS['muted']};font-size:10px;font-weight:bold;"
            f"text-transform:uppercase;"
        )
        return lbl

    def _separator(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color:{COLORS['border']};")
        return sep

    # ── Roll logic ────────────────────────────────────────────────────────

    def _quick_roll(self, die: str) -> None:
        count = self.count_spin.value()
        mod   = self.mod_spin.value()
        expr  = f"{count}{die}"
        if mod > 0:
            expr += f"+{mod}"
        elif mod < 0:
            expr += str(mod)
        self._emit(expr)

    def _roll_custom(self) -> None:
        expr = self.expr_edit.text().strip()
        if not expr:
            return
        self._emit(expr)

    def _emit(self, expr: str) -> None:
        is_private = self.private_cb.isChecked()
        self.roll_requested.emit(expr, is_private)

    def show_last_result(self, formatted: str) -> None:
        self._last_lbl.setText(formatted)
