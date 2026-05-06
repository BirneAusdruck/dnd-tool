"""
VTT View – the main Virtual Tabletop widget.
Contains: GM toolbar, zoomable map canvas, initiative panel.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView,
    QPushButton, QLabel, QSlider, QFileDialog, QSpinBox,
    QToolButton, QButtonGroup, QFrame, QSizePolicy, QMessageBox,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QWheelEvent, QMouseEvent

import requests

from src.gui.theme import COLORS
from src.gui.widgets.map_scene import MapScene, Tool
from src.gui.widgets.initiative_panel import InitiativePanel
from src.gui.widgets.token_item import TOKEN_COLORS, SIZE_LABELS


# ── Zoomable map view ─────────────────────────────────────────────────────

class MapView(QGraphicsView):
    """QGraphicsView with Ctrl+Scroll zoom and middle-mouse pan."""

    MIN_ZOOM = 0.15
    MAX_ZOOM = 4.0

    def __init__(self, scene: MapScene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing |
            QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setBackgroundBrush(Qt.GlobalColor.black)
        self._panning = False
        self._pan_start = None
        self._zoom_level = 1.0

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            factor = 1.18 if event.angleDelta().y() > 0 else 1 / 1.18
            new_zoom = self._zoom_level * factor
            if self.MIN_ZOOM <= new_zoom <= self.MAX_ZOOM:
                self._zoom_level = new_zoom
                self.scale(factor, factor)
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._panning and self._pan_start:
            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def zoom_to_fit(self):
        self.fitInView(self.scene().sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self._zoom_level = self.transform().m11()

    def reset_zoom(self):
        self.resetTransform()
        self._zoom_level = 1.0


# ── Tool button helper ────────────────────────────────────────────────────

def _tool_btn(label: str, tooltip: str, checkable: bool = True) -> QToolButton:
    btn = QToolButton()
    btn.setText(label)
    btn.setToolTip(tooltip)
    btn.setCheckable(checkable)
    btn.setFixedHeight(32)
    btn.setStyleSheet(
        f"QToolButton{{background:{COLORS['surface']};color:{COLORS['text']};border:1px solid {COLORS['border']};border-radius:4px;padding:4px 8px;}}"
        f"QToolButton:checked{{background:{COLORS['accent']};color:white;border-color:{COLORS['accent']};}}"
        f"QToolButton:hover{{background:{COLORS['overlay']};}}"
    )
    return btn


def _action_btn(label: str, tooltip: str = "") -> QPushButton:
    btn = QPushButton(label)
    btn.setToolTip(tooltip)
    btn.setObjectName("secondary-btn")
    btn.setFixedHeight(32)
    return btn


def _sep() -> QFrame:
    sep = QFrame()
    sep.setFrameShape(QFrame.Shape.VLine)
    sep.setStyleSheet(f"color:{COLORS['border']};")
    sep.setFixedWidth(1)
    return sep


# ── Main VTT View ─────────────────────────────────────────────────────────

class VTTView(QWidget):
    def __init__(self, base_url: str, parent=None):
        super().__init__(parent)
        self.base_url = base_url
        self._auth_token: str | None = None
        self._is_gm = True
        self._session_active = False

        self._scene = MapScene(grid_size=50, is_gm=True)
        self._connect_scene_signals()

        self._build_ui()

    def set_auth(self, token: str | None, is_gm: bool = True) -> None:
        self._auth_token = token
        self._is_gm = is_gm
        self._set_gm_controls_visible(is_gm)

    # ── UI construction ───────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Toolbar
        toolbar = self._build_toolbar()
        root.addWidget(toolbar)

        # Main area: canvas + initiative panel
        main_area = QHBoxLayout()
        main_area.setContentsMargins(0, 0, 0, 0)
        main_area.setSpacing(0)

        self._map_view = MapView(self._scene)
        main_area.addWidget(self._map_view, 1)

        # Right panel (initiative)
        right_panel = QWidget()
        right_panel.setFixedWidth(230)
        right_panel.setStyleSheet(f"background:{COLORS['sidebar']};border-left:1px solid {COLORS['border']};")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self._initiative = InitiativePanel()
        right_layout.addWidget(self._initiative)

        main_area.addWidget(right_panel)
        root.addLayout(main_area, 1)

        # Status bar
        self._status_bar = self._build_status_bar()
        root.addWidget(self._status_bar)

    def _build_toolbar(self) -> QWidget:
        bar = QWidget()
        bar.setStyleSheet(f"background:{COLORS['sidebar']};border-bottom:1px solid {COLORS['border']};")
        bar.setFixedHeight(44)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        # ── Map section ──
        self._btn_load_map = _action_btn("🗺 Karte laden", "Bild als Karte laden")
        self._btn_load_map.clicked.connect(self._load_map)
        layout.addWidget(self._btn_load_map)

        layout.addWidget(_sep())

        # ── Tool section ──
        tool_group = QButtonGroup(self)
        tool_group.setExclusive(True)

        self._btn_select = _tool_btn("↖ Auswahl", "Token bewegen / auswählen")
        self._btn_select.setChecked(True)
        self._btn_select.clicked.connect(lambda: self._scene.set_tool(Tool.SELECT))

        self._btn_reveal = _tool_btn("👁 Aufdecken", "Nebel aufdecken")
        self._btn_reveal.clicked.connect(lambda: self._scene.set_tool(Tool.FOG_REVEAL))

        self._btn_hide = _tool_btn("🌑 Verbergen", "Nebel setzen")
        self._btn_hide.clicked.connect(lambda: self._scene.set_tool(Tool.FOG_HIDE))

        self._btn_ping = _tool_btn("📍 Ping", "Ort markieren (alle sehen es)")
        self._btn_ping.clicked.connect(lambda: self._scene.set_tool(Tool.PING))

        for btn in (self._btn_select, self._btn_reveal, self._btn_hide, self._btn_ping):
            tool_group.addButton(btn)
            layout.addWidget(btn)

        layout.addWidget(_sep())

        # ── Fog section ──
        btn_reveal_all = _action_btn("Alles aufdecken")
        btn_reveal_all.clicked.connect(self._scene.reveal_all_fog)
        btn_hide_all = _action_btn("Alles verbergen")
        btn_hide_all.clicked.connect(self._scene.hide_all_fog)

        lbl_brush = QLabel("Pinsel:")
        lbl_brush.setStyleSheet(f"color:{COLORS['muted']};font-size:12px;")
        self._brush_spin = QSpinBox()
        self._brush_spin.setRange(0, 5)
        self._brush_spin.setValue(1)
        self._brush_spin.setFixedWidth(52)
        self._brush_spin.setToolTip("Pinselradius (Kacheln)")
        self._brush_spin.valueChanged.connect(self._scene.set_fog_brush_radius)

        layout.addWidget(btn_reveal_all)
        layout.addWidget(btn_hide_all)
        layout.addWidget(lbl_brush)
        layout.addWidget(self._brush_spin)

        layout.addWidget(_sep())

        # ── Token section ──
        btn_add_token = _action_btn("+ Token", "Token hinzufügen")
        btn_add_token.clicked.connect(self._add_token)
        btn_remove_token = _action_btn("− Token", "Ausgewählten Token entfernen")
        btn_remove_token.clicked.connect(self._remove_selected_token)
        layout.addWidget(btn_add_token)
        layout.addWidget(btn_remove_token)

        layout.addWidget(_sep())

        # ── Grid section ──
        lbl_grid = QLabel("Gitter:")
        lbl_grid.setStyleSheet(f"color:{COLORS['muted']};font-size:12px;")
        self._grid_spin = QSpinBox()
        self._grid_spin.setRange(20, 200)
        self._grid_spin.setValue(50)
        self._grid_spin.setSuffix(" px")
        self._grid_spin.setFixedWidth(72)
        self._grid_spin.setToolTip("Gittergröße in Pixel (Standard: 50px = 5 Fuß)")
        self._grid_spin.valueChanged.connect(self._scene.set_grid_size)
        layout.addWidget(lbl_grid)
        layout.addWidget(self._grid_spin)

        layout.addStretch()

        # ── View section ──
        btn_fit = _action_btn("Einpassen", "Karte in Ansicht einpassen")
        btn_fit.clicked.connect(lambda: self._map_view.zoom_to_fit())
        btn_reset_zoom = _action_btn("100%", "Zoom zurücksetzen")
        btn_reset_zoom.clicked.connect(lambda: self._map_view.reset_zoom())
        layout.addWidget(btn_fit)
        layout.addWidget(btn_reset_zoom)

        # Store GM-only controls for visibility toggling
        self._gm_controls = [
            self._btn_load_map, self._btn_reveal, self._btn_hide,
            btn_reveal_all, btn_hide_all, lbl_brush, self._brush_spin,
            btn_add_token, btn_remove_token, lbl_grid, self._grid_spin,
        ]

        return bar

    def _build_status_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(24)
        bar.setStyleSheet(f"background:{COLORS['sidebar']};border-top:1px solid {COLORS['border']};")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(8, 0, 8, 0)

        self._status_lbl = QLabel("Keine Karte geladen  |  Ctrl+Scrollen zum Zoomen  |  Mittlere Maustaste zum Verschieben")
        self._status_lbl.setStyleSheet(f"color:{COLORS['muted']};font-size:11px;")
        layout.addWidget(self._status_lbl)
        layout.addStretch()

        self._coord_lbl = QLabel("")
        self._coord_lbl.setStyleSheet(f"color:{COLORS['muted']};font-size:11px;")
        layout.addWidget(self._coord_lbl)

        # Hover tracker
        self._map_view.setMouseTracking(True)
        self._map_view.viewport().installEventFilter(self)

        return bar

    # ── Event filter (coordinate display) ────────────────────────────────

    def eventFilter(self, watched, event):
        if watched is self._map_view.viewport():
            from PySide6.QtCore import QEvent
            if event.type() == QEvent.Type.MouseMove:
                scene_pos = self._map_view.mapToScene(event.pos())
                gs = self._grid_spin.value()
                col = int(scene_pos.x()) // gs
                row = int(scene_pos.y()) // gs
                self._coord_lbl.setText(
                    f"({col}, {row})  |  {int(scene_pos.x())}×{int(scene_pos.y())} px"
                )
        return super().eventFilter(watched, event)

    # ── Actions ───────────────────────────────────────────────────────────

    def _load_map(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Karte laden", "",
            "Bilder (*.png *.jpg *.jpeg *.bmp *.webp *.gif);;Alle Dateien (*)"
        )
        if not path:
            return
        if not self._scene.load_map(path):
            QMessageBox.warning(self, "Fehler", "Konnte die Karte nicht laden.")
            return
        self._map_view.zoom_to_fit()
        self._status_lbl.setText(f"Karte: {path.split('/')[-1]}")
        self._push_state()

    def _add_token(self):
        if not self._scene.has_map():
            QMessageBox.information(self, "Hinweis", "Bitte zuerst eine Karte laden.")
            return
        from src.gui.dialogs.token_dialog import TokenDialog
        dlg = TokenDialog(self._auth_token, self.base_url, parent=self)
        if dlg.exec():
            td = dlg.result_data()
            gs = self._grid_spin.value()
            center = self._map_view.mapToScene(
                self._map_view.viewport().rect().center()
            )
            # Snap to grid
            x = round(center.x() / gs) * gs
            y = round(center.y() / gs) * gs
            self._scene.add_token(
                token_id=td["token_id"],
                name=td["name"],
                color=td["color"],
                size=td["size"],
                hp_max=td["hp_max"],
                x=x, y=y,
                char_id=td.get("char_id"),
            )
            self._push_state()

    def _remove_selected_token(self):
        for item in self._scene.selectedItems():
            from src.gui.widgets.token_item import TokenItem
            if isinstance(item, TokenItem):
                self._scene.remove_token(item.token_id)
        self._push_state()

    def _set_gm_controls_visible(self, visible: bool):
        for w in self._gm_controls:
            w.setVisible(visible)

    # ── Server sync ───────────────────────────────────────────────────────

    def _connect_scene_signals(self):
        self._scene.token_moved_sig.connect(self._on_token_moved)
        self._scene.fog_changed_sig.connect(self._on_fog_changed)
        self._scene.map_loaded_sig.connect(self._on_map_loaded)

    def _on_token_moved(self, token_id: str, x: float, y: float):
        self._push_state_debounced()

    def _on_fog_changed(self, changes: list):
        self._push_state_debounced()

    def _on_map_loaded(self, path: str, w: int, h: int, gs: int):
        self._push_state_debounced()

    def _push_state_debounced(self):
        if not hasattr(self, "_push_timer"):
            self._push_timer = QTimer(self)
            self._push_timer.setSingleShot(True)
            self._push_timer.timeout.connect(self._push_state)
        self._push_timer.start(300)

    def _push_state(self):
        if not self._auth_token:
            return
        state = {
            "map_path": self._scene._map_path,
            "grid_size": self._grid_spin.value(),
            "tokens": self._scene.all_tokens(),
            "fog_hidden": self._scene.fog_state(),
            "initiative": self._initiative.get_state(),
        }
        try:
            requests.put(
                f"{self.base_url}/api/vtt/state",
                json=state,
                headers={"Authorization": f"Bearer {self._auth_token}"},
                timeout=2,
            )
        except Exception:
            pass  # Fail silently — state is local anyway

    def load_state(self, state: dict):
        """Restore VTT state (e.g. when reconnecting)."""
        if state.get("map_path"):
            self._scene.load_map(state["map_path"])
        for t in state.get("tokens", []):
            self._scene.add_token(**t)
        if state.get("fog_hidden") is not None:
            self._scene.apply_fog_state(state["fog_hidden"])
        if state.get("initiative"):
            self._initiative.set_state(state["initiative"])
        if state.get("grid_size"):
            self._grid_spin.setValue(state["grid_size"])
