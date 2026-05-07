"""
Token graphic item for the VTT canvas.
Uses QGraphicsObject so it can emit Qt signals.
"""
from __future__ import annotations
import uuid

from PySide6.QtWidgets import QGraphicsObject, QGraphicsItem
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QBrush

# Pixels token occupies per size (relative to grid_size)
SIZE_MULTIPLIERS: dict[str, float] = {
    "tiny":       0.5,
    "small":      0.75,
    "medium":     1.0,
    "large":      2.0,
    "huge":       3.0,
    "gargantuan": 4.0,
}

SIZE_LABELS = list(SIZE_MULTIPLIERS.keys())

# Predefined token colors
TOKEN_COLORS = [
    "#e74c3c", "#3498db", "#2ecc71", "#f39c12",
    "#9b59b6", "#1abc9c", "#e67e22", "#34495e",
    "#e91e63", "#00bcd4", "#8bc34a", "#ff5722",
]


class TokenItem(QGraphicsObject):
    """A draggable, snap-to-grid token on the VTT map."""

    moved = Signal(str, float, float)   # token_id, scene_x, scene_y
    selected_changed = Signal(str, bool)

    def __init__(
        self,
        token_id: str,
        name: str,
        color: str,
        size: str = "medium",
        hp_max: int = 10,
        hp_current: int = 10,
        grid_size: int = 50,
        is_gm: bool = True,
        char_id: int | None = None,
    ):
        super().__init__()
        self.token_id = token_id
        self.name = name
        self.color = QColor(color)
        self.size_name = size
        self.hp_max = hp_max
        self.hp_current = hp_current
        self.grid_size = grid_size
        self.is_gm = is_gm
        self.char_id = char_id

        mult = SIZE_MULTIPLIERS.get(size, 1.0)
        self._radius = (grid_size * mult) / 2.0 - 3.0

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, is_gm)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setZValue(20)
        self.setCursor(Qt.CursorShape.SizeAllCursor if is_gm else Qt.CursorShape.ArrowCursor)

    # ── Qt overrides ──────────────────────────────────────────────────────

    def boundingRect(self) -> QRectF:
        r = self._radius + 4
        return QRectF(-r, -r, r * 2, r * 2)

    def paint(self, painter: QPainter, option, widget=None):
        r = self._radius
        selected = self.isSelected()

        # Selection ring
        if selected:
            painter.setPen(QPen(QColor(255, 220, 50), 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPointF(0, 0), r + 2, r + 2)

        # Main circle
        lighter = self.color.lighter(130)
        painter.setBrush(QBrush(self.color))
        border_color = QColor(255, 255, 255, 180) if not selected else QColor(255, 220, 50)
        painter.setPen(QPen(border_color, 2))
        painter.drawEllipse(QPointF(0, 0), r, r)

        # Highlight arc (top-left glow)
        painter.setBrush(QBrush(lighter))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(-r * 0.3, -r * 0.3), r * 0.45, r * 0.45)

        # Name label (first 4 chars or abbreviated)
        label = self.name[:4] if len(self.name) > 4 else self.name
        font = QFont()
        font.setPixelSize(max(8, int(r * 0.5)))
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QPen(QColor(255, 255, 255, 230)))
        painter.drawText(QRectF(-r, -r * 0.6, r * 2, r * 1.2), Qt.AlignmentFlag.AlignCenter, label)

        # HP bar (bottom strip)
        if self.hp_max > 0:
            bar_w = r * 2
            bar_h = max(4, int(r * 0.15))
            bar_y = r - bar_h - 1
            ratio = max(0.0, min(1.0, self.hp_current / self.hp_max))
            if ratio > 0.5:
                hp_color = QColor(60, 200, 60)
            elif ratio > 0.25:
                hp_color = QColor(220, 200, 30)
            else:
                hp_color = QColor(220, 50, 50)
            painter.fillRect(QRectF(-r, bar_y, bar_w, bar_h), QColor(0, 0, 0, 160))
            painter.fillRect(QRectF(-r, bar_y, bar_w * ratio, bar_h), hp_color)

    # ── Snap-to-grid ──────────────────────────────────────────────────────

    def itemChange(self, change, value):
        if change == QGraphicsObject.GraphicsItemChange.ItemPositionChange:
            gs = self.grid_size
            mult = SIZE_MULTIPLIERS.get(self.size_name, 1.0)
            # Snap center to grid squares (center of occupied area)
            snapped_x = round(value.x() / gs) * gs
            snapped_y = round(value.y() / gs) * gs
            return QPointF(snapped_x, snapped_y)

        if change == QGraphicsObject.GraphicsItemChange.ItemPositionHasChanged:
            self.moved.emit(self.token_id, self.x(), self.y())

        return super().itemChange(change, value)

    # ── Public helpers ────────────────────────────────────────────────────

    def set_hp(self, current: int) -> None:
        self.hp_current = current
        self.update()

    def set_movable(self, movable: bool) -> None:
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, movable)
        self.setCursor(Qt.CursorShape.SizeAllCursor if movable else Qt.CursorShape.ArrowCursor)

    def to_dict(self) -> dict:
        return {
            "token_id": self.token_id,
            "name": self.name,
            "color": self.color.name(),
            "size": self.size_name,
            "hp_max": self.hp_max,
            "hp_current": self.hp_current,
            "x": self.x(),
            "y": self.y(),
            "char_id": self.char_id,
        }

    @staticmethod
    def new_id() -> str:
        return str(uuid.uuid4())[:8]
