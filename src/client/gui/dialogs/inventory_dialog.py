"""
InventoryAddDialog — lets users browse SRD items by category and add them
to a character's inventory.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QListWidget, QListWidgetItem,
    QLineEdit, QTextEdit, QSpinBox, QDialogButtonBox, QSplitter,
)
from PySide6.QtCore import Qt

from src.shared.services.item_service import ItemService
from src.client.gui.theme import COLORS


class InventoryAddDialog(QDialog):
    """Browse SRD items across four categories and add one to the inventory."""

    def __init__(self, char_data: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gegenstand hinzufügen")
        self.setMinimumSize(800, 560)
        self.result_entry: dict = {}
        self._selected_item: dict | None = None
        self._selected_type: str = ""
        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        # Search bar (shared across tabs)
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("Suche:"))
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("Name filtern …")
        self._search_edit.textChanged.connect(self._on_search_changed)
        search_row.addWidget(self._search_edit, 1)
        root.addLayout(search_row)

        # Main splitter: left=tabs+list, right=detail
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: tab widget with item lists
        self._tabs = QTabWidget()
        self._tabs.currentChanged.connect(self._on_tab_changed)

        self._list_weapons   = self._make_list()
        self._list_armor     = self._make_list()
        self._list_equipment = self._make_list()
        self._list_magic     = self._make_list()

        self._tabs.addTab(self._list_weapons,   "Waffen")
        self._tabs.addTab(self._list_armor,     "Rüstungen")
        self._tabs.addTab(self._list_equipment, "Ausrüstung")
        self._tabs.addTab(self._list_magic,     "Magisch")

        splitter.addWidget(self._tabs)

        # Right: detail view
        self._detail = QTextEdit()
        self._detail.setReadOnly(True)
        self._detail.setPlaceholderText("← Item auswählen für Details")
        splitter.addWidget(self._detail)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        root.addWidget(splitter, 1)

        # Bottom: quantity + buttons
        bottom = QHBoxLayout()
        bottom.addWidget(QLabel("Anzahl:"))
        self._qty_spin = QSpinBox()
        self._qty_spin.setRange(1, 99)
        self._qty_spin.setValue(1)
        bottom.addWidget(self._qty_spin)
        bottom.addStretch()

        self._btn_add = QPushButton("Hinzufügen")
        self._btn_add.setObjectName("primary-btn")
        self._btn_add.setEnabled(False)
        self._btn_add.clicked.connect(self._on_add)

        btn_cancel = QPushButton("Abbrechen")
        btn_cancel.setObjectName("secondary-btn")
        btn_cancel.clicked.connect(self.reject)

        bottom.addWidget(btn_cancel)
        bottom.addWidget(self._btn_add)
        root.addLayout(bottom)

        # Populate all lists
        self._populate_all()

    def _make_list(self) -> QListWidget:
        lst = QListWidget()
        lst.currentItemChanged.connect(self._on_item_selected)
        return lst

    # ── Data population ───────────────────────────────────────────────────

    def _populate_all(self) -> None:
        self._populate_weapons()
        self._populate_armor()
        self._populate_equipment()
        self._populate_magic()

    def _populate_weapons(self, filter_text: str = "") -> None:
        self._list_weapons.clear()
        for w in sorted(ItemService.get_all_weapons_raw(), key=lambda x: x["name"]):
            if filter_text and filter_text.lower() not in w["name"].lower():
                continue
            dmg = f"{w['damage']} {w['damage_type']}" if w.get("damage") else "—"
            display = f"{w['name']}  [{w['category']}]  {dmg}"
            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, ("weapon", w))
            self._list_weapons.addItem(item)

    def _populate_armor(self, filter_text: str = "") -> None:
        self._list_armor.clear()
        for a in sorted(ItemService.get_all_armor_raw(), key=lambda x: x["name"]):
            if filter_text and filter_text.lower() not in a["name"].lower():
                continue
            ac_str = str(a["base_ac"])
            if a.get("dex_bonus"):
                max_d = a.get("max_dex")
                ac_str += f"+DEX{f'(max {max_d})' if max_d is not None else ''}"
            display = f"{a['name']}  [{a['category']}]  RK {ac_str}"
            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, ("armor", a))
            self._list_armor.addItem(item)

    def _populate_equipment(self, filter_text: str = "") -> None:
        self._list_equipment.clear()
        for e in ItemService.get_all_equipment_raw():
            if filter_text and filter_text.lower() not in e["name"].lower():
                continue
            display = f"{e['name']}  [{e['category']}]  {e['cost']}"
            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, ("equipment", e))
            self._list_equipment.addItem(item)

    def _populate_magic(self, filter_text: str = "") -> None:
        self._list_magic.clear()
        for m in ItemService.get_all_magic_items_raw():
            if filter_text and filter_text.lower() not in m["name"].lower():
                continue
            att = " [Einstimmung]" if m.get("attunement") else ""
            display = f"{m['name']}  [{m['rarity']}]{att}"
            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, ("magic-item", m))
            self._list_magic.addItem(item)

    # ── Event handlers ────────────────────────────────────────────────────

    def _on_search_changed(self, text: str) -> None:
        idx = self._tabs.currentIndex()
        if idx == 0:
            self._populate_weapons(text)
        elif idx == 1:
            self._populate_armor(text)
        elif idx == 2:
            self._populate_equipment(text)
        elif idx == 3:
            self._populate_magic(text)

    def _on_tab_changed(self, _index: int) -> None:
        self._search_edit.clear()
        self._detail.clear()
        self._selected_item = None
        self._selected_type = ""
        self._btn_add.setEnabled(False)

    def _on_item_selected(self, current: QListWidgetItem | None, _prev) -> None:
        if not current:
            self._selected_item = None
            self._selected_type = ""
            self._btn_add.setEnabled(False)
            self._detail.clear()
            return

        item_type, item_data = current.data(Qt.ItemDataRole.UserRole)
        self._selected_item = item_data
        self._selected_type = item_type
        self._btn_add.setEnabled(True)
        self._show_detail(item_type, item_data)

    def _show_detail(self, item_type: str, item: dict) -> None:
        lines = []
        if item_type == "weapon":
            lines.append(f"<b>{item['name']}</b>  <i>({item['category']})</i>")
            if item.get("damage"):
                lines.append(f"Schaden: {item['damage']} {item['damage_type']}")
            if item.get("damage_versatile"):
                lines.append(f"Vielseitig: {item['damage_versatile']}")
            if item.get("range"):
                lines.append(f"Reichweite: {item['range']}")
            if item.get("properties"):
                lines.append(f"Eigenschaften: {', '.join(item['properties'])}")
            if item.get("mastery"):
                lines.append(f"Mastery: {item['mastery']}")
            lines.append(f"Gewicht: {item['weight']} lb  |  Kosten: {item['cost']}")
        elif item_type == "armor":
            lines.append(f"<b>{item['name']}</b>  <i>({item['category']} armor)</i>")
            ac_str = str(item["base_ac"])
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
            lines.append(f"<b>{item['name']}</b>  <i>({item['category']})</i>")
            lines.append(f"Gewicht: {item['weight']} lb  |  Kosten: {item['cost']}")
        elif item_type == "magic-item":
            lines.append(f"<b>{item['name']}</b>")
            lines.append(f"Seltenheit: {item['rarity'].capitalize()}")
            lines.append(f"Kategorie: {item['category']}")
            if item.get("attunement"):
                att = item["attunement"]
                att_str = att if isinstance(att, str) else "Ja"
                lines.append(f"Einstimmung: {att_str}")
        lines.append("")
        lines.append(item.get("desc", ""))
        self._detail.setHtml("<br>".join(lines))

    def _on_add(self) -> None:
        if not self._selected_item:
            return
        item = self._selected_item
        self.result_entry = {
            "item_index": item["index"],
            "item_type":  self._selected_type,
            "name":       item["name"],
            "quantity":   self._qty_spin.value(),
            "equipped":   False,
            "attuned":    False,
            "notes":      "",
        }
        self.accept()


class EquipSlotDialog(QDialog):
    """Select one inventory entry to equip in a slot."""

    def __init__(self, candidates: list[dict], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gegenstand ausrüsten")
        self.setMinimumSize(480, 360)
        self.selected_entry: dict | None = None
        self._candidates = candidates
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self._list = QListWidget()
        for entry in self._candidates:
            list_item = QListWidgetItem(entry.get("name", entry.get("item_index", "?")))
            list_item.setData(Qt.ItemDataRole.UserRole, entry)
            self._list.addItem(list_item)
        self._list.currentItemChanged.connect(self._on_selected)
        splitter.addWidget(self._list)

        self._detail = QTextEdit()
        self._detail.setReadOnly(True)
        self._detail.setPlaceholderText("← Item auswählen")
        splitter.addWidget(self._detail)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        root.addWidget(splitter, 1)

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Abbrechen")
        btn_cancel.setObjectName("secondary-btn")
        btn_cancel.clicked.connect(self.reject)
        self._btn_equip = QPushButton("Ausrüsten")
        self._btn_equip.setObjectName("primary-btn")
        self._btn_equip.setEnabled(False)
        self._btn_equip.clicked.connect(self._on_equip)
        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(self._btn_equip)
        root.addLayout(btn_row)

    def _on_selected(self, current, _prev) -> None:
        if not current:
            self._detail.clear()
            self._btn_equip.setEnabled(False)
            return
        self._btn_equip.setEnabled(True)
        entry = current.data(Qt.ItemDataRole.UserRole)
        lines = [f"<b>{entry.get('name', '?')}</b>"]
        lines.append(f"Typ: {entry.get('item_type', '?')}")
        qty = entry.get("quantity", 1)
        if qty > 1:
            lines.append(f"Anzahl: {qty}")
        if entry.get("notes"):
            lines.append(f"<i>{entry['notes']}</i>")
        self._detail.setHtml("<br>".join(lines))

    def _on_equip(self) -> None:
        list_item = self._list.currentItem()
        if not list_item:
            return
        self.selected_entry = list_item.data(Qt.ItemDataRole.UserRole)
        self.accept()
