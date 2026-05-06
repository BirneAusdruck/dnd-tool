"""
Level-up / level-down logic for DnD 5e characters.
Pure stateless functions — takes char_data dicts and returns new dicts.

Data contract additions (all backwards-compatible):
  basics.classes     – list[{class_index, level, subclass}]  (multiclassing ready)
  basics.asi_history – list[{total_level, class_index, changes}]
  hp.level_history   – list[int]  (HP gained at each level, index 0 = level 1)
"""

from __future__ import annotations
import copy

from src.game.srd_loader import get_class, get_class_spell_slots
from src.game.character_builder import modifier


# ── ASI Detection ──────────────────────────────────────────────────────────

_DEFAULT_ASI_LEVELS: set[int] = {4, 8, 12, 16, 19}


def get_asi_levels(class_index: str) -> set[int]:
    """Return the set of levels at which this class gains an ASI."""
    cls = get_class(class_index)
    if not cls:
        return _DEFAULT_ASI_LEVELS
    asi = {
        int(lvl)
        for lvl, feats in cls["features"].items()
        for feat in feats
        if "Ability Score Improvement" in feat
    }
    return asi or _DEFAULT_ASI_LEVELS


def get_new_features(class_index: str, level: int) -> list[str]:
    """Return the class features gained at exactly this level."""
    cls = get_class(class_index)
    if not cls:
        return []
    return list(cls["features"].get(str(level), []))


# ── Multiclassing-Ready Field Bootstrap ────────────────────────────────────

def ensure_level_fields(data: dict) -> dict:
    """
    Ensure char_data has the multiclassing-ready fields.
    Mutates the dict in place (call on a deepcopy).
    """
    basics = data["basics"]

    if "classes" not in basics:
        basics["classes"] = [{
            "class_index": basics["class"],
            "level": basics["level"],
            "subclass": basics.get("subclass"),
        }]

    if "asi_history" not in basics:
        basics["asi_history"] = []

    if "feats" not in basics:
        basics["feats"] = []

    if "feat_history" not in basics:
        basics["feat_history"] = []

    hp = data.setdefault("hp", {})
    if "level_history" not in hp:
        level = basics["level"]
        hp["level_history"] = [hp.get("max", 0)] + [0] * (level - 1)

    return data


# ── Queries ────────────────────────────────────────────────────────────────

def can_level_up(char_data: dict) -> bool:
    return char_data["basics"]["level"] < 20


def can_level_down(char_data: dict) -> bool:
    return char_data["basics"]["level"] > 1


def primary_class(char_data: dict) -> str:
    """Return the primary class index (first in classes list, or basics.class)."""
    classes = char_data["basics"].get("classes")
    if classes:
        return classes[0]["class_index"]
    return char_data["basics"].get("class", "")


# ── Level-Up Info (for the dialog) ────────────────────────────────────────

def get_level_up_info(char_data: dict) -> dict:
    """
    Return all information the LevelUpDialog needs to display choices.
    Does NOT modify char_data.
    """
    data = ensure_level_fields(copy.deepcopy(char_data))
    basics = data["basics"]
    cls_idx = primary_class(data)
    current_level = basics["level"]
    new_level = current_level + 1

    cls = get_class(cls_idx)
    hit_die = cls["hit_die"] if cls else 8
    con_mod = modifier(data["ability_scores"].get("CON", 10))

    new_features = get_new_features(cls_idx, new_level)
    is_asi = new_level in get_asi_levels(cls_idx)

    # Spellcasting changes
    spell_info = None
    if cls and cls.get("spellcasting"):
        sc = cls["spellcasting"]
        old_slots = get_class_spell_slots(cls_idx, current_level)
        new_slots = get_class_spell_slots(cls_idx, new_level)

        cntrp = sc.get("cantrips_known", [])
        old_cantrips = cntrp[current_level - 1] if current_level <= len(cntrp) else 0
        new_cantrips = cntrp[new_level - 1] if new_level <= len(cntrp) else 0
        gained_cantrip = new_cantrips > old_cantrips

        new_spell_count = 0
        if sc["type"] == "known":
            known = sc.get("spells_known", [])
            old_known = known[current_level - 1] if current_level <= len(known) else 0
            new_known = known[new_level - 1] if new_level <= len(known) else 0
            new_spell_count = max(0, new_known - old_known)

        spell_info = {
            "ability": sc["ability"],
            "type": sc["type"],
            "old_slots": old_slots,
            "new_slots": new_slots,
            "gained_cantrip": gained_cantrip,
            "new_spell_count": new_spell_count,
        }

    return {
        "class_index": cls_idx,
        "current_level": current_level,
        "new_level": new_level,
        "hit_die": hit_die,
        "con_mod": con_mod,
        "hp_average": max(1, hit_die // 2 + 1 + con_mod),
        "new_features": new_features,
        "is_asi": is_asi,
        "spell_info": spell_info,
        "current_scores": dict(data["ability_scores"]),
    }


# ── Level Down Info (for the confirmation dialog) ─────────────────────────

def get_level_down_info(char_data: dict) -> dict:
    """Return summary of what will be undone when removing the current level."""
    data = ensure_level_fields(copy.deepcopy(char_data))
    basics = data["basics"]
    cls_idx = primary_class(data)
    current_level = basics["level"]

    features_at_level = get_new_features(cls_idx, current_level)
    is_asi_level = current_level in get_asi_levels(cls_idx)

    # Find the last ASI applied at this level
    last_asi = None
    if is_asi_level:
        for entry in reversed(basics.get("asi_history", [])):
            if entry["total_level"] == current_level:
                last_asi = entry["changes"]
                break

    # HP to remove
    level_history = data["hp"].get("level_history", [])
    hp_to_remove = level_history[-1] if len(level_history) >= current_level else 0

    # Find the last Feat taken at this level
    last_feat = None
    for entry in reversed(basics.get("feat_history", [])):
        if entry["total_level"] == current_level:
            last_feat = entry["feat_index"]
            break

    return {
        "current_level": current_level,
        "new_level": current_level - 1,
        "class_index": cls_idx,
        "hp_to_remove": hp_to_remove,
        "features_removed": features_at_level,
        "asi_undone": last_asi,
        "feat_undone": last_feat,
    }


# ── Apply Level-Up ─────────────────────────────────────────────────────────

def apply_level_up(
    char_data: dict,
    hp_gain: int,
    asi_changes: dict[str, int] | None = None,
    feat_index: str | None = None,
) -> dict:
    """
    Return a new char_data dict with the level-up applied.

    hp_gain:     total HP to add (caller already includes CON mod)
    asi_changes: e.g. {"STR": 2} or {"STR": 1, "DEX": 1}, or None
    feat_index:  index of chosen feat (mutually exclusive with asi_changes)
    """
    data = ensure_level_fields(copy.deepcopy(char_data))
    basics = data["basics"]
    cls_idx = primary_class(data)
    new_level = basics["level"] + 1

    # Level counter
    basics["level"] = new_level
    basics["classes"][0]["level"] = new_level

    # Hit dice string
    cls = get_class(cls_idx)
    hit_die = cls["hit_die"] if cls else 8
    data["hit_dice"]["total"] = f"{new_level}d{hit_die}"

    # HP
    hp = data["hp"]
    hp["max"] += hp_gain
    hp["current"] += hp_gain
    hp["level_history"].append(hp_gain)

    # ASI or Feat (mutually exclusive)
    if feat_index:
        if feat_index not in basics["feats"]:
            basics["feats"].append(feat_index)
        basics["feat_history"].append({
            "total_level": new_level,
            "class_index": cls_idx,
            "feat_index": feat_index,
        })
    elif asi_changes:
        for ab, delta in asi_changes.items():
            if ab in data["ability_scores"]:
                data["ability_scores"][ab] = min(20, data["ability_scores"][ab] + delta)
        basics["asi_history"].append({
            "total_level": new_level,
            "class_index": cls_idx,
            "changes": dict(asi_changes),
        })

    return data


# ── Apply Level-Down ───────────────────────────────────────────────────────

def apply_level_down(char_data: dict) -> dict:
    """
    Return a new char_data dict with the last level removed.
    Reverses the most recent level-up: undoes HP and ASI from that level.
    """
    data = ensure_level_fields(copy.deepcopy(char_data))
    basics = data["basics"]

    if basics["level"] <= 1:
        return data

    cls_idx = primary_class(data)
    removed_level = basics["level"]

    # Undo Feat if one was taken at this level
    feat_history: list[dict] = basics.get("feat_history", [])
    if feat_history and feat_history[-1]["total_level"] == removed_level:
        last_feat = feat_history.pop()
        feat_idx = last_feat["feat_index"]
        if feat_idx in basics.get("feats", []):
            basics["feats"].remove(feat_idx)

    # Undo ASI if one was recorded for this level
    asi_history: list[dict] = basics.get("asi_history", [])
    if asi_history and asi_history[-1]["total_level"] == removed_level:
        last_asi = asi_history.pop()
        for ab, delta in last_asi["changes"].items():
            if ab in data["ability_scores"]:
                data["ability_scores"][ab] = max(1, data["ability_scores"][ab] - delta)

    # Remove HP gained at this level
    level_history: list[int] = data["hp"].get("level_history", [])
    if len(level_history) >= removed_level:
        hp_removed = level_history.pop()
        data["hp"]["max"] = max(1, data["hp"]["max"] - hp_removed)
        data["hp"]["current"] = min(data["hp"]["current"], data["hp"]["max"])

    # Decrement level
    new_level = removed_level - 1
    basics["level"] = new_level
    basics["classes"][0]["level"] = new_level

    # Hit dice string
    cls = get_class(cls_idx)
    hit_die = cls["hit_die"] if cls else 8
    data["hit_dice"]["total"] = f"{new_level}d{hit_die}"

    return data
