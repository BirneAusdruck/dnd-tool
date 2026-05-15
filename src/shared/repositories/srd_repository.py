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
    _load_dict_file.cache_clear()
    _refresh_default()


def get_active_edition() -> str:
    return _active_edition


@lru_cache(maxsize=None)
def _load_dict_file(edition: str, filename: str) -> dict:
    """Load a flat dict-structured JSON file (e.g. {key: [values]}) with layer merging."""
    sources = _EDITION_SOURCES.get(edition, _EDITION_SOURCES["5.1_srd"])
    merged: dict = {}
    for source_dir in sources:
        path = source_dir / filename
        if not path.exists():
            continue
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            merged.update(data)
    return merged


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

    def get_traits(self) -> list[dict]:
        return self._get_list("traits.json")

    def get_trait(self, index: str) -> dict | None:
        return next((t for t in self.get_traits() if t["index"] == index), None)

    def get_subraces_list(self) -> list[dict]:
        return self._get_list("subraces.json")

    def get_subrace_by_index(self, index: str) -> dict | None:
        return next((s for s in self.get_subraces_list() if s["index"] == index), None)

    def get_subrace(self, race_index: str, subrace_index: str) -> dict | None:
        return self.get_subrace_by_index(subrace_index)

    # ── Classes ────────────────────────────────────────────────────────────

    def get_classes(self) -> list[dict]:
        return self._get_list("classes.json")

    def get_class(self, index: str) -> dict | None:
        return next((c for c in self.get_classes() if c["index"] == index), None)

    def get_subclass_groups(self) -> list[dict]:
        return self._get_list("subclasses.json")

    def get_subclass_group(self, index: str) -> dict | None:
        return next((s for s in self.get_subclass_groups() if s["index"] == index), None)

    def get_subclass_group_for_class(self, class_index: str) -> dict | None:
        return next((s for s in self.get_subclass_groups() if s.get("class") == class_index), None)

    def get_class_starting_equipments(self) -> list[dict]:
        return self._get_list("class_starting_equipments.json")

    def get_class_starting_equipment(self, index: str) -> dict | None:
        return next((e for e in self.get_class_starting_equipments() if e["index"] == index), None)

    def get_features(self, class_index: str | None = None) -> list[dict]:
        items = self._get_list("features.json")
        if class_index:
            items = [f for f in items if f.get("class") == class_index]
        return items

    def get_feature(self, index: str) -> dict | None:
        return next((f for f in self._get_list("features.json") if f["index"] == index), None)

    def get_effects(self) -> list[dict]:
        return self._get_list("effects.json")

    def get_effect(self, index: str) -> dict | None:
        return next((e for e in self.get_effects() if e["index"] == index), None)

    # ── Backgrounds ────────────────────────────────────────────────────────

    def get_backgrounds(self) -> list[dict]:
        return self._get_list("backgrounds.json")

    def get_background(self, index: str) -> dict | None:
        return next((b for b in self.get_backgrounds() if b["index"] == index), None)

    def get_background_features(self) -> list[dict]:
        return self._get_list("background_features.json")

    def get_background_feature(self, index: str) -> dict | None:
        return next((f for f in self.get_background_features() if f["index"] == index), None)

    def get_background_equipment_entries(self) -> list[dict]:
        return self._get_list("background_equipment_entries.json")

    def get_background_equipment_entry(self, index: str) -> dict | None:
        return next((e for e in self.get_background_equipment_entries() if e["index"] == index), None)

    def get_background_personality_traits(self) -> list[dict]:
        return self._get_list("background_personality_traits.json")

    def get_background_personality_trait(self, group_index: str) -> dict | None:
        return next((g for g in self.get_background_personality_traits() if g["index"] == group_index), None)

    def get_background_ideals(self) -> list[dict]:
        return self._get_list("background_ideals.json")

    def get_background_ideal(self, group_index: str) -> dict | None:
        return next((g for g in self.get_background_ideals() if g["index"] == group_index), None)

    def get_background_bonds(self) -> list[dict]:
        return self._get_list("background_bonds.json")

    def get_background_bond(self, group_index: str) -> dict | None:
        return next((g for g in self.get_background_bonds() if g["index"] == group_index), None)

    def get_background_flaws(self) -> list[dict]:
        return self._get_list("background_flaws.json")

    def get_background_flaw(self, group_index: str) -> dict | None:
        return next((g for g in self.get_background_flaws() if g["index"] == group_index), None)

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

    def get_spell(self, index: str) -> dict | None:
        return next(
            (s for s in self._get_list("spells.json")
             if s.get("index") == index or s["name"].lower() == index.lower()),
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
def get_traits() -> list[dict]:                           return _default.get_traits()
def get_trait(index: str) -> dict | None:                 return _default.get_trait(index)
def get_subraces_list() -> list[dict]:                    return _default.get_subraces_list()
def get_subrace_by_index(index: str) -> dict | None:      return _default.get_subrace_by_index(index)
def get_subrace(r: str, s: str) -> dict | None:           return _default.get_subrace(r, s)
def get_classes() -> list[dict]:                          return _default.get_classes()
def get_class(index: str) -> dict | None:                 return _default.get_class(index)
def get_backgrounds() -> list[dict]:                      return _default.get_backgrounds()
def get_background(index: str) -> dict | None:            return _default.get_background(index)
def get_background_features() -> list[dict]:              return _default.get_background_features()
def get_background_feature(index: str) -> dict | None:    return _default.get_background_feature(index)
def get_background_equipment_entries() -> list[dict]:     return _default.get_background_equipment_entries()
def get_background_equipment_entry(index: str) -> dict | None: return _default.get_background_equipment_entry(index)
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
def get_background_personality_traits() -> list[dict]:                 return _default.get_background_personality_traits()
def get_background_personality_trait(idx: str) -> dict | None:         return _default.get_background_personality_trait(idx)
def get_background_ideals() -> list[dict]:                             return _default.get_background_ideals()
def get_background_ideal(idx: str) -> dict | None:                     return _default.get_background_ideal(idx)
def get_background_bonds() -> list[dict]:                              return _default.get_background_bonds()
def get_background_bond(idx: str) -> dict | None:                      return _default.get_background_bond(idx)
def get_background_flaws() -> list[dict]:                              return _default.get_background_flaws()
def get_background_flaw(idx: str) -> dict | None:                      return _default.get_background_flaw(idx)
