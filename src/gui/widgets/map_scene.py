"""
MapScene – QGraphicsScene subclass that orchestrates the entire VTT canvas.

Layer z-values:
  0   background map pixmap
  10  grid overlay
  20  token items
  30  fog-of-war overlay
  40  measurement / ping overlay (future)
"""
from __future__ import annotations
from enum import Enum

from PySide6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QGraphicsEllipseItem
from PySide6.QtCore import Qt, QPointF, Signal
from PySide6.QtGui import QPixmap, QColor, QPen

from src.gui.widgets.token_item import TokenItem, TOKEN_COLORS
from src.gui.widgets.fog_overlay import FogOverlay, GridOverlay


class Tool(Enum):
    SELECT     = "select"
    FOG_REVEAL = "fog_reveal"
    FOG_HIDE   = "fog_hide"
    PING       = "ping"


class MapScene(QGraphicsScene):
    # Signals for SocketIO / REST sync
    token_moved_sig  = Signal(str, float, float)        # id, x, y
    fog_changed_sig  = Signal(list)                     # [(row, col, hidden), ...]
    map_loaded_sig   = Signal(str, int, int, int)       # path, w, h, grid_size
    token_added_sig  = Signal(dict)
    token_removed_sig = Signal(str)

    def __init__(self, grid_size: int = 50, is_gm: bool = True):
        super().__init__()
        self._grid_size = grid_size
        self._is_gm = is_gm
        self._tool = Tool.SELECT
        self._fog_brush_radius = 1   # tiles around cursor to paint
        self._fog_painting = False

        self._map_item:  QGraphicsPixmapItem | None = None
        self._grid_item: GridOverlay | None = None
        self._fog_item:  FogOverlay  | None = None
        self._tokens:    dict[str, TokenItem] = {}
        self._color_counter = 0

        self._map_path = ""
        self._map_width = 0
        self._map_height = 0

        # Show empty placeholder
        self.setSceneRect(0, 0, 800, 600)
        self.setBackgroundBrush(QColor(30, 30, 40))

    # ── Map loading ───────────────────────────────────────────────────────

    def load_map(self, path: str) -> bool:
        pixmap = QPixmap(path)
        if pixmap.isNull():
            return False

        self._map_path = path
        self._map_width = pixmap.width()
        self._map_height = pixmap.height()

        self.clear()
        self._tokens.clear()

        self.setSceneRect(0, 0, self._map_width, self._map_height)

        self._map_item = QGraphicsPixmapItem(pixmap)
        self._map_item.setZValue(0)
        self.addItem(self._map_item)

        self._grid_item = GridOverlay(self._map_width, self._map_height, self._grid_size)
        self.addItem(self._grid_item)

        self._fog_item = FogOverlay(
            self._map_width, self._map_height, self._grid_size, gm_view=self._is_gm
        )
        self.addItem(self._fog_item)

        self.map_loaded_sig.emit(path, self._map_width, self._map_height, self._grid_size)
        return True

    def has_map(self) -> bool:
        return self._map_item is not None

    # ── Tool management ───────────────────────────────────────────────────

    def set_tool(self, tool: Tool) -> None:
        self._tool = tool
        movable = tool == Tool.SELECT
        for token in self._tokens.values():
            token.set_movable(movable and self._is_gm)

    def set_grid_size(self, size: int) -> None:
        self._grid_size = size
        if self._grid_item:
            self._grid_item._grid_size = size
            self._grid_item.update()
        if self._fog_item:
            self._fog_item._grid_size = size
            self._fog_item.resize(self._map_width, self._map_height)
        for token in self._tokens.values():
            token.grid_size = size

    def set_fog_brush_radius(self, radius: int) -> None:
        self._fog_brush_radius = radius

    # ── Token management ──────────────────────────────────────────────────

    def add_token(
        self,
        token_id: str,
        name: str,
        color: str,
        size: str = "medium",
        hp_max: int = 10,
        hp_current: int | None = None,
        x: float = 0.0,
        y: float = 0.0,
        char_id: int | None = None,
        movable: bool = True,
    ) -> TokenItem:
        if hp_current is None:
            hp_current = hp_max

        token = TokenItem(
            token_id=token_id,
            name=name,
            color=color,
            size=size,
            hp_max=hp_max,
            hp_current=hp_current,
            grid_size=self._grid_size,
            is_gm=self._is_gm and movable,
            char_id=char_id,
        )
        token.setPos(x, y)
        token.moved.connect(self._on_token_moved)
        self.addItem(token)
        self._tokens[token_id] = token
        self.token_added_sig.emit(token.to_dict())
        return token

    def remove_token(self, token_id: str) -> None:
        token = self._tokens.pop(token_id, None)
        if token:
            self.removeItem(token)
            self.token_removed_sig.emit(token_id)

    def update_token_hp(self, token_id: str, current_hp: int) -> None:
        token = self._tokens.get(token_id)
        if token:
            token.set_hp(current_hp)

    def apply_token_move(self, token_id: str, x: float, y: float) -> None:
        """Apply a move received from SocketIO (no re-emit)."""
        token = self._tokens.get(token_id)
        if token:
            token.blockSignals(True)
            token.setPos(x, y)
            token.blockSignals(False)

    def next_color(self) -> str:
        color = TOKEN_COLORS[self._color_counter % len(TOKEN_COLORS)]
        self._color_counter += 1
        return color

    def all_tokens(self) -> list[dict]:
        return [t.to_dict() for t in self._tokens.values()]

    # ── Fog management ────────────────────────────────────────────────────

    def reveal_all_fog(self) -> None:
        if self._fog_item:
            self._fog_item.reveal_all()
            self.fog_changed_sig.emit([])

    def hide_all_fog(self) -> None:
        if self._fog_item:
            self._fog_item.hide_all()
            if self._fog_item._rows and self._fog_item._cols:
                all_cells = [(r, c, True) for r in range(self._fog_item._rows)
                             for c in range(self._fog_item._cols)]
                self.fog_changed_sig.emit(all_cells)

    def apply_fog_state(self, hidden_cells: list[list[int]]) -> None:
        if self._fog_item:
            self._fog_item.set_state(hidden_cells)

    def fog_state(self) -> list[list[int]]:
        return self._fog_item.get_state() if self._fog_item else []

    # ── Mouse events ──────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if self._tool in (Tool.FOG_REVEAL, Tool.FOG_HIDE) and self._fog_item:
            self._fog_painting = True
            self._paint_fog_at(event.scenePos())
            event.accept()
            return
        if self._tool == Tool.PING:
            self._show_ping(event.scenePos())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._fog_painting and self._fog_item:
            self._paint_fog_at(event.scenePos())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._fog_painting = False
        super().mouseReleaseEvent(event)

    # ── Private helpers ───────────────────────────────────────────────────

    def _paint_fog_at(self, scene_pos: QPointF) -> None:
        if not self._fog_item:
            return
        row, col = self._fog_item.tile_at(scene_pos.x(), scene_pos.y())
        hidden = self._tool == Tool.FOG_HIDE
        changes = self._fog_item.set_brush(row, col, self._fog_brush_radius, hidden)
        if changes:
            self.fog_changed_sig.emit(changes)

    def _on_token_moved(self, token_id: str, x: float, y: float) -> None:
        self.token_moved_sig.emit(token_id, x, y)

    def _show_ping(self, pos: QPointF) -> None:
        """Flash a ping circle at the given position."""
        ping = QGraphicsEllipseItem(pos.x() - 20, pos.y() - 20, 40, 40)
        ping.setPen(QPen(QColor(255, 200, 50, 200), 3))
        ping.setZValue(40)
        self.addItem(ping)
        # Remove after a short delay (use QTimer via the view)
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1200, lambda: self.removeItem(ping) if ping.scene() else None)
