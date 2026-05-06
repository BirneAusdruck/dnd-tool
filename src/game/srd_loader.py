import json
from pathlib import Path
from functools import lru_cache

_DATA_ROOT = Path(__file__).parent.parent.parent / "data"

# Source directories per edition, ordered lowest → highest priority.
# When the same index appears in multiple sources, the later (higher-priority)
# entry wins. This allows PHB/ADV/custom to override or extend the SRD.
_EDITION_SOURCES: dict[str, list[Path]] = {
    # SRD only — bare minimum, no PHB content
    "5.1_srd": [
        _DATA_ROOT / "srd" / "5.1",
    ],
    "5.2_srd": [
        _DATA_ROOT / "srd" / "5.2",
    ],
    # SRD Custom Ruleset
    "5.1_srd_custom": [
        _DATA_ROOT / "srd" / "5.1",
        _DATA_ROOT / "custom",
    ],
    "5.2_srd_custom": [
        _DATA_ROOT / "srd" / "5.2",
        _DATA_ROOT / "custom",
    ],
    # Basic (free rules) only
    "5e_basic": [
        _DATA_ROOT / "dnd" / "5.0e" / "basic",
    ],
    "5.5e_basic": [
        _DATA_ROOT / "dnd" / "5.5e" / "basic",
    ],
    # PHB = SRD baseline + basic + PHB (+ custom overrides)
    "5e_phb": [
        _DATA_ROOT / "srd"  / "5.1",
        _DATA_ROOT / "dnd"  / "5.0e" / "basic",
        _DATA_ROOT / "dnd"  / "5.0e" / "phb",
    ],
    "5.5e_phb": [
        _DATA_ROOT / "srd"  / "5.2",
        _DATA_ROOT / "dnd"  / "5.5e" / "basic",
        _DATA_ROOT / "dnd"  / "5.5e" / "phb",
    ],
    "5e_adv": [
        _DATA_ROOT / "srd"  / "5.1",
        _DATA_ROOT / "dnd"  / "5.0e" / "basic",
        _DATA_ROOT / "dnd"  / "5.0e" / "phb",
        _DATA_ROOT / "dnd"  / "5.0e" / "adv", 
    ],
    "5.5e_adv": [
        _DATA_ROOT / "srd"  / "5.2",
        _DATA_ROOT / "dnd"  / "5.5e" / "basic",
        _DATA_ROOT / "dnd"  / "5.5e" / "phb",
        _DATA_ROOT / "dnd"  / "5.5e" / "adv",
    ],
}

_active_edition: str = "5.1_srd"


def set_edition(edition: str) -> None:
    global _active_edition
    if edition not in _EDITION_SOURCES:
        return
    _active_edition = edition
    _load_merged.cache_clear()


def get_active_edition() -> str:
    return _active_edition


@lru_cache(maxsize=None)
def _load_merged(edition: str, filename: str) -> dict:
    """Merge all available source files for an edition.

    Items are keyed by 'index' (or 'name' as fallback).
    Higher-priority sources override lower-priority entries with the same key.
    """
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


def _get_list(filename: str) -> list[dict]:
    data = _load_merged(_active_edition, filename)
    return next(iter(data.values()), []) if data else []


# ── Races ──────────────────────────────────────────────────────────────────

def get_races() -> list[dict]:
    return _get_list("races.json")


def get_race(index: str) -> dict | None:
    return next((r for r in get_races() if r["index"] == index), None)


def get_subrace(race_index: str, subrace_index: str) -> dict | None:
    race = get_race(race_index)
    if not race:
        return None
    return next((s for s in race.get("subraces", []) if s["index"] == subrace_index), None)


# ── Classes ────────────────────────────────────────────────────────────────

def get_classes() -> list[dict]:
    return _get_list("classes.json")


def get_class(index: str) -> dict | None:
    return next((c for c in get_classes() if c["index"] == index), None)


def get_class_features(class_index: str, level: int) -> list[str]:
    cls = get_class(class_index)
    if not cls:
        return []
    features = []
    for lvl in range(1, level + 1):
        features.extend(cls["features"].get(str(lvl), []))
    return features


def get_class_spell_slots(class_index: str, level: int) -> list[int]:
    cls = get_class(class_index)
    if not cls or not cls.get("spellcasting"):
        return []
    slots = cls["spellcasting"]["slots"]
    idx = min(level - 1, len(slots) - 1)
    return slots[idx]


# ── Backgrounds ────────────────────────────────────────────────────────────

def get_backgrounds() -> list[dict]:
    return _get_list("backgrounds.json")


def get_background(index: str) -> dict | None:
    return next((b for b in get_backgrounds() if b["index"] == index), None)


# ── Spells ─────────────────────────────────────────────────────────────────

def get_spells(class_index: str | None = None, level: int | None = None) -> list[dict]:
    spells = _get_list("spells.json")
    if class_index:
        spells = [s for s in spells if class_index in s.get("classes", [])]
    if level is not None:
        spells = [s for s in spells if s["level"] == level]
    return sorted(spells, key=lambda s: (s["level"], s["name"]))


def get_cantrips(class_index: str) -> list[dict]:
    return get_spells(class_index=class_index, level=0)


def get_spell(name: str) -> dict | None:
    return next(
        (s for s in _get_list("spells.json") if s["name"].lower() == name.lower()),
        None,
    )


# ── Feats ─────────────────────────────────────────────────────────────────

def get_feats() -> list[dict]:
    return _get_list("feats.json")


def get_feat(index: str) -> dict | None:
    return next((f for f in get_feats() if f["index"] == index), None)


# ── Skills (static) ────────────────────────────────────────────────────────

_ICON_ROOT = Path(__file__).parent.parent.parent / "assets/icons"
_ICON_ROOT_SKILL = _ICON_ROOT / "skill"

SKILLS: list[dict] = [
    {"name": "Acrobatics",      "ability": "DEX", "icon":_ICON_ROOT_SKILL / "acrobatics"},
    {"name": "Animal Handling", "ability": "WIS", "icon":_ICON_ROOT_SKILL / "animal-handling"},
    {"name": "Arcana",          "ability": "INT", "icon":_ICON_ROOT_SKILL / "arcana"},
    {"name": "Athletics",       "ability": "STR", "icon":_ICON_ROOT_SKILL / "athletics"},
    {"name": "Deception",       "ability": "CHA", "icon":_ICON_ROOT_SKILL / "deception"},
    {"name": "History",         "ability": "INT", "icon":_ICON_ROOT_SKILL / "history"},
    {"name": "Insight",         "ability": "WIS", "icon":_ICON_ROOT_SKILL / "insight"},
    {"name": "Intimidation",    "ability": "CHA", "icon":_ICON_ROOT_SKILL / "intimidation"},
    {"name": "Investigation",   "ability": "INT", "icon":_ICON_ROOT_SKILL / "investigation"},
    {"name": "Medicine",        "ability": "WIS", "icon":_ICON_ROOT_SKILL / "medicine"},
    {"name": "Nature",          "ability": "INT", "icon":_ICON_ROOT_SKILL / "nature"},
    {"name": "Perception",      "ability": "WIS", "icon":_ICON_ROOT_SKILL / "perception"},
    {"name": "Performance",     "ability": "CHA", "icon":_ICON_ROOT_SKILL / "performance"},
    {"name": "Persuasion",      "ability": "CHA", "icon":_ICON_ROOT_SKILL / "persuasion"},
    {"name": "Religion",        "ability": "INT", "icon":_ICON_ROOT_SKILL / "religion"},
    {"name": "Sleight of Hand", "ability": "DEX", "icon":_ICON_ROOT_SKILL / "sleight-of-hand"},
    {"name": "Stealth",         "ability": "DEX", "icon":_ICON_ROOT_SKILL / "stealth"},
    {"name": "Survival",        "ability": "WIS", "icon":_ICON_ROOT_SKILL / "survival"},
]

_ICON_ROOT_ABILITY = _ICON_ROOT / "ability"

ABILITIES = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
ABILITY_ICONS = {
    "STR": _ICON_ROOT_ABILITY / "strength", 
    "DEX": _ICON_ROOT_ABILITY / "dexterity", 
    "CON": _ICON_ROOT_ABILITY / "constitution", 
    "INT": _ICON_ROOT_ABILITY / "intelligence", 
    "WIS": _ICON_ROOT_ABILITY / "wisdom", 
    "CHA": _ICON_ROOT_ABILITY / "charisma",
    }

ALIGNMENTS = [
    "Lawful Good", "Neutral Good", "Chaotic Good",
    "Lawful Neutral", "True Neutral", "Chaotic Neutral",
    "Lawful Evil", "Neutral Evil", "Chaotic Evil",
]
