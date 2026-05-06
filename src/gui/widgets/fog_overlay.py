"""
Fog-of-War and grid overlay items for the VTT QGraphicsScene.
"""
from __future__ import annotations

from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter, QColor, QPen


class GridOverlay(QGraphicsItem):
    """Draws a semi-transparent square grid over the map."""

    def __init__(self, width: int, height: int, grid_size: int = 50):
        super().__init__()
        self._width = width
        self._height = height
        self._grid_size = grid_size
        self.setZValue(10)
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self._width, self._height)

    def paint(self, painter: QPainter, option, widget=None):
        gs = self._grid_size
        pen = QPen(QColor(200, 200, 200, 45))
        pen.setWidth(1)
        painter.setPen(pen)

        for x in range(0, self._width + gs, gs):
            painter.drawLine(x, 0, x, self._height)
        for y in range(0, self._height + gs, gs):
            painter.drawLine(0, y, self._width, y)

    def resize(self, width: int, height: int) -> None:
        self.prepareGeometryChange()
        self._width = width
        self._height = height
        self.update()


class FogOverlay(QGraphicsItem):
    """
    Tile-based Fog of War.

    Hidden tiles are drawn as dark semi-transparent rectangles.
    The GM sees fog at ~60% opacity (map is still visible through).
    Players (Phase 5) will receive fully opaque fog.
    """

    GM_ALPHA = 160      # GM sees through fog
    PLAYER_ALPHA = 245  # Players see near-black fog

    def __init__(
        self,
        width: int,
        height: int,
        grid_size: int = 50,
        gm_view: bool = True,
    ):
        super().__init__()
        self._width = width
        self._height = height
        self._grid_size = grid_size
        self._gm_view = gm_view
        self._alpha = self.GM_ALPHA if gm_view else self.PLAYER_ALPHA

        self._cols = (width + grid_size - 1) // grid_size
        self._rows = (height + grid_size - 1) // grid_size

        # Start fully hidden
        self._hidden: set[tuple[int, int]] = {
            (r, c) for r in range(self._rows) for c in range(self._cols)
        }

        self.setZValue(30)
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)

    # ── Qt overrides ──────────────────────────────────────────────────────

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self._width, self._height)

    def paint(self, painter: QPainter, option, widget=None):
        if not self._hidden:
            return
        gs = self._grid_size
        fog_color = QColor(15, 15, 20, self._alpha)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(fog_color)
        for (r, c) in self._hidden:
            painter.drawRect(c * gs, r * gs, gs, gs)

    # ── Public API ────────────────────────────────────────────────────────

    def set_tile(self, row: int, col: int, hidden: bool) -> bool:
        """Set a tile's fog state. Returns True if the state changed."""
        if row < 0 or row >= self._rows or col < 0 or col >= self._cols:
            return False
        key = (row, col)
        if hidden and key not in self._hidden:
            self._hidden.add(key)
            self.update(QRectF(col * self._grid_size, row * self._grid_size,
                               self._grid_size, self._grid_size))
            return True
        elif not hidden and key in self._hidden:
            self._hidden.discard(key)
            self.update(QRectF(col * self._grid_size, row * self._grid_size,
                               self._grid_size, self._grid_size))
            return True
        return False

    def set_brush(self, row: int, col: int, radius: int, hidden: bool) -> list[tuple[int, int, bool]]:
        """Paint fog/reveal in a square brush of `radius` tiles. Returns changed cells."""
        changes = []
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                if self.set_tile(row + dr, col + dc, hidden):
                    changes.append((row + dr, col + dc, hidden))
        return changes

    def reveal_all(self) -> None:
        self._hidden.clear()
        self.update()

    def hide_all(self) -> None:
        self._hidden = {
            (r, c) for r in range(self._rows) for c in range(self._cols)
        }
        self.update()

    def set_state(self, hidden_cells: list[list[int]]) -> None:
        """Restore fog state from a serialized list of [row, col] pairs."""
        self._hidden = {(row, col) for row, col in hidden_cells}
        self.update()

    def get_state(self) -> list[list[int]]:
        return [[r, c] for r, c in self._hidden]

    def tile_at(self, scene_x: float, scene_y: float) -> tuple[int, int]:
        gs = self._grid_size
        return int(scene_y) // gs, int(scene_x) // gs

    def resize(self, width: int, height: int) -> None:
        self.prepareGeometryChange()
        self._width = width
        self._height = height
        self._cols = (width + self._grid_size - 1) // self._grid_size
        self._rows = (height + self._grid_size - 1) // self._grid_size
        self.hide_all()
