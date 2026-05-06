import json
from pathlib import Path
from functools import lru_cache

_SRD_DIR = Path(__file__).parent.parent.parent / "data" / "srd"


@lru_cache(maxsize=None)
def _load(filename: str) -> dict | list:
    with open(_SRD_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


# ── Races ──────────────────────────────────────────────────────────────────

def get_races() -> list[dict]:
    return _load("races.json")["races"]


def get_race(index: str) -> dict | None:
    return next((r for r in get_races() if r["index"] == index), None)


def get_subrace(race_index: str, subrace_index: str) -> dict | None:
    race = get_race(race_index)
    if not race:
        return None
    return next((s for s in race.get("subraces", []) if s["index"] == subrace_index), None)


# ── Classes ────────────────────────────────────────────────────────────────

def get_classes() -> list[dict]:
    return _load("classes.json")["classes"]


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
    return _load("backgrounds.json")["backgrounds"]


def get_background(index: str) -> dict | None:
    return next((b for b in get_backgrounds() if b["index"] == index), None)


# ── Spells ─────────────────────────────────────────────────────────────────

def get_spells(class_index: str | None = None, level: int | None = None) -> list[dict]:
    spells = _load("spells.json")["spells"]
    if class_index:
        spells = [s for s in spells if class_index in s.get("classes", [])]
    if level is not None:
        spells = [s for s in spells if s["level"] == level]
    return sorted(spells, key=lambda s: (s["level"], s["name"]))


def get_cantrips(class_index: str) -> list[dict]:
    return get_spells(class_index=class_index, level=0)


def get_spell(name: str) -> dict | None:
    spells = _load("spells.json")["spells"]
    return next((s for s in spells if s["name"].lower() == name.lower()), None)


# ── Skills (static) ────────────────────────────────────────────────────────

SKILLS: list[dict] = [
    {"name": "Acrobatics",     "ability": "DEX"},
    {"name": "Animal Handling","ability": "WIS"},
    {"name": "Arcana",         "ability": "INT"},
    {"name": "Athletics",      "ability": "STR"},
    {"name": "Deception",      "ability": "CHA"},
    {"name": "History",        "ability": "INT"},
    {"name": "Insight",        "ability": "WIS"},
    {"name": "Intimidation",   "ability": "CHA"},
    {"name": "Investigation",  "ability": "INT"},
    {"name": "Medicine",       "ability": "WIS"},
    {"name": "Nature",         "ability": "INT"},
    {"name": "Perception",     "ability": "WIS"},
    {"name": "Performance",    "ability": "CHA"},
    {"name": "Persuasion",     "ability": "CHA"},
    {"name": "Religion",       "ability": "INT"},
    {"name": "Sleight of Hand","ability": "DEX"},
    {"name": "Stealth",        "ability": "DEX"},
    {"name": "Survival",       "ability": "WIS"},
]

ABILITIES = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]

ALIGNMENTS = [
    "Lawful Good", "Neutral Good", "Chaotic Good",
    "Lawful Neutral", "True Neutral", "Chaotic Neutral",
    "Lawful Evil", "Neutral Evil", "Chaotic Evil",
]
