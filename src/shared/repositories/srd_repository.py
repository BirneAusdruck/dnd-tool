from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_DATA_ROOT = Path(__file__).parent.parent.parent.parent / "data"

_EDITION_SOURCES: dict[str, list[Path]] = {
    "5.1_srd": [_DATA_ROOT / "srd" / "5.1"],
    "5.2_srd": [_DATA_ROOT / "srd" / "5.2"],
    "5.1_srd_custom": [_DATA_ROOT / "srd" / "5.1", _DATA_ROOT / "custom"],
    "5.2_srd_custom": [_DATA_ROOT / "srd" / "5.2", _DATA_ROOT / "custom"],
    "5e_basic":  [_DATA_ROOT / "dnd" / "5.0e" / "basic"],
    "5.5e_basic": [_DATA_ROOT / "dnd" / "5.5e" / "basic"],
    "5e_phb": [
        _DATA_ROOT / "srd" / "5.1",
        _DATA_ROOT / "dnd" / "5.0e" / "basic",
        _DATA_ROOT / "dnd" / "5.0e" / "phb",
    ],
    "5.5e_phb": [
        _DATA_ROOT / "srd" / "5.2",
        _DATA_ROOT / "dnd" / "5.5e" / "basic",
        _DATA_ROOT / "dnd" / "5.5e" / "phb",
    ],
    "5e_adv": [
        _DATA_ROOT / "srd" / "5.1",
        _DATA_ROOT / "dnd" / "5.0e" / "basic",
        _DATA_ROOT / "dnd" / "5.0e" / "phb",
        _DATA_ROOT / "dnd" / "5.0e" / "adv",
    ],
    "5.5e_adv": [
        _DATA_ROOT / "srd" / "5.2",
        _DATA_ROOT / "dnd" / "5.5e" / "basic",
        _DATA_ROOT / "dnd" / "5.5e" / "phb",
        _DATA_ROOT / "dnd" / "5.5e" / "adv",
    ],
}

_active_edition: str = "5.1_srd"


def set_edition(edition: str) -> None:
    global _active_edition
    if edition not in _EDITION_SOURCES:
        return
    _active_edition = edition
    _load_merged.cache_clear()
    _refresh_default()


def get_active_edition() -> str:
    return _active_edition


@lru_cache(maxsize=None)
def _load_merged(edition: str, filename: str) -> dict:
    sources = _EDITION_SOURCES.get(edition, _EDITION_SOURCES["5.1_srd"])
    merged: dict[str, dict] = {}
    top_key: str | None = None

    for source_dir in sources:
        path = source_dir / filename
        if not path.exists():
            continue
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            continue
        key, items = next(iter(data.items()))
        top_key = key
        for item in items:
            idx = item.get("index") or item.get("name", "")
            merged[idx] = item

    return {top_key: list(merged.values())} if top_key else {}


# ── Reference Data ─────────────────────────────────────────────────────────

SKILLS: list[dict] = [
    {"name": "Acrobatics",      "ability": "DEX"},
    {"name": "Animal Handling", "ability": "WIS"},
    {"name": "Arcana",          "ability": "INT"},
    {"name": "Athletics",       "ability": "STR"},
    {"name": "Deception",       "ability": "CHA"},
    {"name": "History",         "ability": "INT"},
    {"name": "Insight",         "ability": "WIS"},
    {"name": "Intimidation",    "ability": "CHA"},
    {"name": "Investigation",   "ability": "INT"},
    {"name": "Medicine",        "ability": "WIS"},
    {"name": "Nature",          "ability": "INT"},
    {"name": "Perception",      "ability": "WIS"},
    {"name": "Performance",     "ability": "CHA"},
    {"name": "Persuasion",      "ability": "CHA"},
    {"name": "Religion",        "ability": "INT"},
    {"name": "Sleight of Hand", "ability": "DEX"},
    {"name": "Stealth",         "ability": "DEX"},
    {"name": "Survival",        "ability": "WIS"},
]

ABILITIES = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]

ALIGNMENTS = [
    "Lawful Good", "Neutral Good", "Chaotic Good",
    "Lawful Neutral", "True Neutral", "Chaotic Neutral",
    "Lawful Evil", "Neutral Evil", "Chaotic Evil",
]


# ── Repository Class ───────────────────────────────────────────────────────

class SRDRepository:
    """Data Access Layer — loads and merges SRD JSON, returns raw dicts only."""

    def __init__(self, edition: str | None = None) -> None:
        self._edition = edition or _active_edition

    def _get_list(self, filename: str) -> list[dict]:
        data = _load_merged(self._edition, filename)
        return next(iter(data.values()), []) if data else []

    # ── Races ──────────────────────────────────────────────────────────────

    def get_races(self) -> list[dict]:
        return self._get_list("races.json")

    def get_race(self, index: str) -> dict | None:
        return next((r for r in self.get_races() if r["index"] == index), None)

    def get_subrace(self, race_index: str, subrace_index: str) -> dict | None:
        race = self.get_race(race_index)
        if not race:
            return None
        return next(
            (s for s in race.get("subraces", []) if s["index"] == subrace_index), None
        )

    # ── Classes ────────────────────────────────────────────────────────────

    def get_classes(self) -> list[dict]:
        return self._get_list("classes.json")

    def get_class(self, index: str) -> dict | None:
        return next((c for c in self.get_classes() if c["index"] == index), None)

    # ── Backgrounds ────────────────────────────────────────────────────────

    def get_backgrounds(self) -> list[dict]:
        return self._get_list("backgrounds.json")

    def get_background(self, index: str) -> dict | None:
        return next((b for b in self.get_backgrounds() if b["index"] == index), None)

    # ── Spells ─────────────────────────────────────────────────────────────

    def get_spells(
        self,
        class_index: str | None = None,
        level: int | None = None,
    ) -> list[dict]:
        spells = self._get_list("spells.json")
        if class_index:
            spells = [s for s in spells if class_index in s.get("classes", [])]
        if level is not None:
            spells = [s for s in spells if s["level"] == level]
        return sorted(spells, key=lambda s: (s["level"], s["name"]))

    def get_cantrips(self, class_index: str) -> list[dict]:
        return self.get_spells(class_index=class_index, level=0)

    def get_spell(self, name: str) -> dict | None:
        return next(
            (s for s in self._get_list("spells.json") if s["name"].lower() == name.lower()),
            None,
        )

    # ── Feats ──────────────────────────────────────────────────────────────

    def get_feats(self) -> list[dict]:
        return self._get_list("feats.json")

    def get_feat(self, index: str) -> dict | None:
        return next((f for f in self.get_feats() if f["index"] == index), None)

    # ── Weapons ────────────────────────────────────────────────────────────

    def get_weapons(self) -> list[dict]:
        return self._get_list("weapons.json")

    def get_weapon(self, index: str) -> dict | None:
        return next((w for w in self.get_weapons() if w["index"] == index), None)

    # ── Armor ──────────────────────────────────────────────────────────────

    def get_armor_list(self) -> list[dict]:
        return self._get_list("armor.json")

    def get_armor(self, index: str) -> dict | None:
        return next((a for a in self.get_armor_list() if a["index"] == index), None)

    # ── Equipment ──────────────────────────────────────────────────────────

    def get_equipment_list(self, category: str | None = None) -> list[dict]:
        items = self._get_list("equipment.json")
        if category:
            items = [i for i in items if i.get("category") == category]
        return sorted(items, key=lambda i: i["name"])

    def get_equipment(self, index: str) -> dict | None:
        return next((i for i in self.get_equipment_list() if i["index"] == index), None)

    # ── Magic Items ────────────────────────────────────────────────────────

    def get_magic_items(
        self,
        category: str | None = None,
        rarity: str | None = None,
    ) -> list[dict]:
        items = self._get_list("magic-items.json")
        if category:
            items = [i for i in items if i.get("category") == category]
        if rarity:
            items = [i for i in items if i.get("rarity") == rarity]
        return sorted(items, key=lambda i: i["name"])

    def get_magic_item(self, index: str) -> dict | None:
        return next((i for i in self.get_magic_items() if i["index"] == index), None)


# ── Module-level convenience (delegates to a default instance) ─────────────
# Used by domain/ and gui/ code that imports specific functions by name.

_default = SRDRepository()


def _refresh_default() -> None:
    global _default
    _default = SRDRepository()


def get_races() -> list[dict]:                            return _default.get_races()
def get_race(index: str) -> dict | None:                  return _default.get_race(index)
def get_subrace(r: str, s: str) -> dict | None:           return _default.get_subrace(r, s)
def get_classes() -> list[dict]:                          return _default.get_classes()
def get_class(index: str) -> dict | None:                 return _default.get_class(index)
def get_backgrounds() -> list[dict]:                      return _default.get_backgrounds()
def get_background(index: str) -> dict | None:            return _default.get_background(index)
def get_spells(class_index: str | None = None,
               level: int | None = None) -> list[dict]:   return _default.get_spells(class_index, level)
def get_cantrips(class_index: str) -> list[dict]:         return _default.get_cantrips(class_index)
def get_spell(name: str) -> dict | None:                  return _default.get_spell(name)
def get_feats() -> list[dict]:                            return _default.get_feats()
def get_feat(index: str) -> dict | None:                  return _default.get_feat(index)
def get_weapons() -> list[dict]:                          return _default.get_weapons()
def get_weapon(index: str) -> dict | None:                return _default.get_weapon(index)
def get_armor_list() -> list[dict]:                       return _default.get_armor_list()
def get_armor(index: str) -> dict | None:                 return _default.get_armor(index)
def get_equipment_list(category: str | None = None) -> list[dict]: return _default.get_equipment_list(category)
def get_equipment(index: str) -> dict | None:             return _default.get_equipment(index)
def get_magic_items(category: str | None = None,
                    rarity: str | None = None) -> list[dict]: return _default.get_magic_items(category, rarity)
def get_magic_item(index: str) -> dict | None:            return _default.get_magic_item(index)
