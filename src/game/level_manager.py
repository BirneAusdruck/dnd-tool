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


# ── Multiclass Spellcasting ────────────────────────────────────────────────

# PHB combined spell slot table, index 0 = combined caster level 1
_MULTICLASS_SLOTS: list[list[int]] = [
    [2, 0, 0, 0, 0, 0, 0, 0, 0],  #  1
    [3, 0, 0, 0, 0, 0, 0, 0, 0],  #  2
    [4, 2, 0, 0, 0, 0, 0, 0, 0],  #  3
    [4, 3, 0, 0, 0, 0, 0, 0, 0],  #  4
    [4, 3, 2, 0, 0, 0, 0, 0, 0],  #  5
    [4, 3, 3, 0, 0, 0, 0, 0, 0],  #  6
    [4, 3, 3, 1, 0, 0, 0, 0, 0],  #  7
    [4, 3, 3, 2, 0, 0, 0, 0, 0],  #  8
    [4, 3, 3, 3, 1, 0, 0, 0, 0],  #  9
    [4, 3, 3, 3, 2, 0, 0, 0, 0],  # 10
    [4, 3, 3, 3, 2, 1, 0, 0, 0],  # 11
    [4, 3, 3, 3, 2, 1, 0, 0, 0],  # 12
    [4, 3, 3, 3, 2, 1, 1, 0, 0],  # 13
    [4, 3, 3, 3, 2, 1, 1, 0, 0],  # 14
    [4, 3, 3, 3, 2, 1, 1, 1, 0],  # 15
    [4, 3, 3, 3, 2, 1, 1, 1, 0],  # 16
    [4, 3, 3, 3, 2, 1, 1, 1, 1],  # 17
    [4, 3, 3, 3, 3, 1, 1, 1, 1],  # 18
    [4, 3, 3, 3, 3, 2, 1, 1, 1],  # 19
    [4, 3, 3, 3, 3, 2, 2, 1, 1],  # 20
]

# Warlock pact slot level by warlock class level (not included in class JSON)
_PACT_SLOT_LEVEL: list[int] = [
    1, 1, 2, 2, 3, 3, 4, 4, 5, 5,
    5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
]


def get_class_caster_weight(class_index: str, subclass: str | None = None) -> float | str:
    """
    Return the multiclass caster weight for a class:
      1.0   = full caster (Wizard, Cleric …)
      0.5   = half caster (Paladin, Ranger)
      1/3   = third caster (Eldritch Knight, Arcane Trickster)
      "pact" = Warlock (Pact Magic, tracked separately)
      0.0   = non-caster
    Derived from the slot table in the SRD data, no hardcoding needed.
    """
    cls = get_class(class_index)
    if not cls or not cls.get("spellcasting"):
        # Fighter/Rogue gain spellcasting only via subclass
        if class_index == "fighter" and subclass and "Eldritch Knight" in subclass:
            return 1 / 3
        if class_index == "rogue" and subclass and "Arcane Trickster" in subclass:
            return 1 / 3
        return 0.0
    sc = cls["spellcasting"]
    if sc.get("type") == "pact":
        return "pact"
    # Half-casters have no slots at class level 1 (first entry is [0])
    if sc.get("slots") and sc["slots"][0][0] == 0:
        return 0.5
    return 1.0


def get_combined_caster_level(classes: list[dict]) -> int:
    """
    Sum all non-pact caster levels weighted by caster type (floor the total).
    classes: list of {"class_index": ..., "level": ..., "subclass": ...}
    """
    total = 0.0
    for c in classes:
        weight = get_class_caster_weight(c["class_index"], c.get("subclass"))
        if isinstance(weight, float) and weight > 0:
            total += c["level"] * weight
    return int(total)  # floor


def get_multiclass_spell_slots(combined_caster_level: int) -> list[int]:
    """Return combined spell slots from the PHB multiclass table."""
    if combined_caster_level <= 0:
        return []
    idx = min(combined_caster_level - 1, len(_MULTICLASS_SLOTS) - 1)
    return list(_MULTICLASS_SLOTS[idx])


def get_pact_slots(warlock_level: int) -> tuple[int, int]:
    """Return (count, slot_level) of pact slots at the given warlock level."""
    if warlock_level <= 0:
        return (0, 0)
    idx = min(warlock_level - 1, len(_PACT_SLOT_LEVEL) - 1)
    cls = get_class("warlock")
    count = cls["spellcasting"]["slots"][idx][0] if cls else 0
    return (count, _PACT_SLOT_LEVEL[idx])


def is_multiclass_spellcaster(classes: list[dict]) -> bool:
    """True if the character has 2+ non-pact spellcasting classes."""
    return sum(
        1 for c in classes
        if get_class_caster_weight(c["class_index"], c.get("subclass")) not in (0.0, "pact")
    ) > 1


def get_cantrip_scaling_tier(total_level: int) -> int:
    """
    Return the cantrip damage multiplier (1–4) based on total character level.
    Cantrips scale with CHARACTER level, not class level.
    """
    if total_level >= 17:
        return 4
    if total_level >= 11:
        return 3
    if total_level >= 5:
        return 2
    return 1


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

    # Tracks which class was leveled at each total level — needed for correct level-down
    if "level_history" not in basics:
        basics["level_history"] = []

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

def has_char_class(char_data : dict, cls_idx: str):
    classes = char_data["basics"].get("classes")
    return cls_idx in classes
        

def select_class(char_data: dict, cls_idx: str| None):
    if cls_idx:
        return primary_class(char_data)
    
    if has_char_class(char_data, cls_idx):
        return cls_idx

# ── Level-Up Info (for the dialog) ────────────────────────────────────────

def get_level_up_info(char_data: dict, class_index: str | None = None) -> dict:
    """
    Return all information the LevelUpDialog needs to display choices.
    Does NOT modify char_data.

    Returned fields:
      total_level      – current total character level
      new_total_level  – total level after this level-up
      class_level      – current level in the chosen class (0 if brand-new multiclass)
      new_class_level  – class level after this level-up (used for features/ASI/spells)
      current_level    – alias for total_level  (backward compat)
      new_level        – alias for new_total_level (backward compat)
    """
    data = ensure_level_fields(copy.deepcopy(char_data))
    basics = data["basics"]
    cls_idx = class_index if class_index else primary_class(data)

    total_level = basics["level"]
    new_total_level = total_level + 1

    # Level within the chosen class (0 when multiclassing into a brand-new class)
    cls_entry = next(
        (c for c in basics["classes"] if c["class_index"] == cls_idx), None
    )
    class_level = cls_entry["level"] if cls_entry else 0
    new_class_level = class_level + 1

    cls = get_class(cls_idx)
    hit_die = cls["hit_die"] if cls else 8
    con_mod = modifier(data["ability_scores"].get("CON", 10))

    # All class-specific lookups use new_class_level, not total level
    new_features = get_new_features(cls_idx, new_class_level)
    is_asi = new_class_level in get_asi_levels(cls_idx)

    # Subclass selection: triggered exactly once when reaching subclass_level
    is_subclass = (
        cls is not None
        and new_class_level == cls["subclass_level"]
        and (cls_entry is None or not cls_entry.get("subclass"))
    )
    subclass_choices: list[str] = cls["subclasses"] if is_subclass else []

    # Spellcasting changes
    spell_info = None
    classes_list = basics["classes"]

    # Build a simulated "after" class list to compute new combined caster level
    after_classes = [
        {**c, "level": c["level"] + 1} if c["class_index"] == cls_idx
        else c
        for c in classes_list
    ]
    if cls_idx not in {c["class_index"] for c in classes_list}:
        # Brand-new multiclass entry
        after_classes = list(classes_list) + [
            {"class_index": cls_idx, "level": 1, "subclass": None}
        ]

    multiclass = is_multiclass_spellcaster(after_classes)

    # Warlock pact slots (always separate)
    warlock_entry = next((c for c in classes_list if c["class_index"] == "warlock"), None)
    old_pact = get_pact_slots(warlock_entry["level"] if warlock_entry else 0)
    warlock_after = next((c for c in after_classes if c["class_index"] == "warlock"), None)
    new_pact = get_pact_slots(warlock_after["level"] if warlock_after else 0)

    if cls and cls.get("spellcasting"):
        sc = cls["spellcasting"]

        if multiclass:
            # Combined slot table
            old_combined = get_combined_caster_level(classes_list)
            new_combined = get_combined_caster_level(after_classes)
            old_slots = get_multiclass_spell_slots(old_combined)
            new_slots = get_multiclass_spell_slots(new_combined)
        else:
            old_slots = get_class_spell_slots(cls_idx, class_level)
            new_slots = get_class_spell_slots(cls_idx, new_class_level)

        cntrp = sc.get("cantrips_known", [])
        old_cantrips = cntrp[class_level - 1] if 0 < class_level <= len(cntrp) else 0
        new_cantrips = cntrp[new_class_level - 1] if new_class_level <= len(cntrp) else 0
        gained_cantrip = new_cantrips > old_cantrips

        new_spell_count = 0
        if sc["type"] == "known":
            known = sc.get("spells_known", [])
            old_known = known[class_level - 1] if 0 < class_level <= len(known) else 0
            new_known = known[new_class_level - 1] if new_class_level <= len(known) else 0
            new_spell_count = max(0, new_known - old_known)

        spell_info = {
            "ability": sc["ability"],
            "type": sc["type"],
            "is_multiclass": multiclass,
            "old_slots": old_slots,
            "new_slots": new_slots,
            "old_pact": old_pact,
            "new_pact": new_pact,
            "gained_cantrip": gained_cantrip,
            "new_spell_count": new_spell_count,
        }
    elif old_pact != new_pact:
        # Warlock leveling as non-primary caster or gaining pact slots
        spell_info = {
            "ability": "CHA",
            "type": "pact",
            "is_multiclass": multiclass,
            "old_slots": [],
            "new_slots": [],
            "old_pact": old_pact,
            "new_pact": new_pact,
            "gained_cantrip": False,
            "new_spell_count": 0,
        }

    return {
        "class_index": cls_idx,
        "total_level": total_level,
        "new_total_level": new_total_level,
        "class_level": class_level,
        "new_class_level": new_class_level,
        # backward-compatible aliases
        "current_level": total_level,
        "new_level": new_total_level,
        "hit_die": hit_die,
        "con_mod": con_mod,
        "hp_average": max(1, hit_die // 2 + 1 + con_mod),
        "new_features": new_features,
        "is_asi": is_asi,
        "is_subclass": is_subclass,
        "subclass_name": cls["subclass_name"] if cls else "",
        "subclass_choices": subclass_choices,
        "spell_info": spell_info,
        "current_scores": dict(data["ability_scores"]),
    }


# ── Level Down Info (for the confirmation dialog) ─────────────────────────

def get_level_down_info(char_data: dict) -> dict:
    """Return summary of what will be undone when removing the current level."""
    data = ensure_level_fields(copy.deepcopy(char_data))
    basics = data["basics"]
    total_level = basics["level"]

    # Which class was leveled last?
    lvl_hist = basics.get("level_history", [])
    if lvl_hist and lvl_hist[-1]["total_level"] == total_level:
        cls_idx = lvl_hist[-1]["class_index"]
    else:
        cls_idx = primary_class(data)

    # Class-specific level for features lookup
    cls_entry = next((c for c in basics["classes"] if c["class_index"] == cls_idx), None)
    class_level = cls_entry["level"] if cls_entry else total_level

    features_at_level = get_new_features(cls_idx, class_level)

    # ASI undone at this total level
    last_asi = None
    for entry in reversed(basics.get("asi_history", [])):
        if entry["total_level"] == total_level:
            last_asi = entry["changes"]
            break

    # HP to remove
    hp_level_history = data["hp"].get("level_history", [])
    hp_to_remove = hp_level_history[-1] if len(hp_level_history) >= total_level else 0

    # Feat undone at this total level
    last_feat = None
    for entry in reversed(basics.get("feat_history", [])):
        if entry["total_level"] == total_level:
            last_feat = entry["feat_index"]
            break

    # Subclass undone if class was at exactly its subclass level
    cls_data = get_class(cls_idx)
    subclass_undone = (
        cls_data is not None
        and cls_entry is not None
        and cls_entry["level"] == cls_data.get("subclass_level")
        and cls_entry.get("subclass")
    )

    return {
        "current_level": total_level,
        "new_level": total_level - 1,
        "class_index": cls_idx,
        "class_level": class_level,
        "hp_to_remove": hp_to_remove,
        "features_removed": features_at_level,
        "asi_undone": last_asi,
        "feat_undone": last_feat,
        "subclass_undone": cls_entry.get("subclass") if subclass_undone else None,
    }


# ── Apply Level-Up ─────────────────────────────────────────────────────────

def apply_level_up(
    char_data: dict,
    hp_gain: int,
    class_index: str,
    asi_changes: dict[str, int] | None = None,
    feat_index: str | None = None,
    subclass_index: str | None = None,
) -> dict:
    """
    Return a new char_data dict with the level-up applied.

    hp_gain:       total HP to add (caller already includes CON mod)
    asi_changes:   e.g. {"STR": 2} or {"STR": 1, "DEX": 1}, or None
    feat_index:    index of chosen feat (mutually exclusive with asi_changes)
    subclass_index: subclass name chosen at the subclass level
    """



    data = ensure_level_fields(copy.deepcopy(char_data))
    basics = data["basics"]
    # Suche ob class_index schon in basics.classes existiert
    entry = next((c for c in basics["classes"] if c["class_index"] == class_index), None)
    # Level counter
    if entry:
        entry["level"] += 1       # bestehende Klasse aufleveln
    else:
        basics["classes"].append( # neue Klasse hinzufügen
            {"class_index": class_index, "level": 1, "subclass": None}
        )
    basics["level"] += 1          # Gesamtlevel immer +1
    new_level = basics["level"]

    # Record which class was leveled — needed for correct multiclass level-down
    basics["level_history"].append({"total_level": new_level, "class_index": class_index})

    # Hit dice string
    cls = get_class(class_index)
    hit_die = cls["hit_die"] if cls else 8
    data["hit_dice"]["total"] = f"{new_level}d{hit_die}"

    # HP
    hp = data["hp"]
    hp["max"] += hp_gain
    hp["current"] += hp_gain
    hp["level_history"].append(hp_gain)

    # Subclass
    if subclass_index:
        target = next((c for c in basics["classes"] if c["class_index"] == class_index), None)
        if target is not None:
            target["subclass"] = subclass_index

    # ASI or Feat (mutually exclusive)
    if feat_index:
        if feat_index not in basics["feats"]:
            basics["feats"].append(feat_index)
        basics["feat_history"].append({
            "total_level": new_level,
            "class_index": class_index,
            "feat_index": feat_index,
        })
    elif asi_changes:
        for ab, delta in asi_changes.items():
            if ab in data["ability_scores"]:
                data["ability_scores"][ab] = min(20, data["ability_scores"][ab] + delta)
        basics["asi_history"].append({
            "total_level": new_level,
            "class_index": class_index,
            "changes": dict(asi_changes),
        })

    return data


# ── Apply Level-Down ───────────────────────────────────────────────────────

def apply_level_down(char_data: dict) -> dict:
    """
    Return a new char_data dict with the last level removed.
    Uses basics.level_history to know which class was leveled last,
    so multiclass level-down is correct.
    """
    data = ensure_level_fields(copy.deepcopy(char_data))
    basics = data["basics"]

    if basics["level"] <= 1:
        return data

    removed_level = basics["level"]

    # Determine which class was leveled last
    lvl_hist: list[dict] = basics.get("level_history", [])
    if lvl_hist and lvl_hist[-1]["total_level"] == removed_level:
        cls_idx = lvl_hist.pop()["class_index"]
    else:
        cls_idx = primary_class(data)  # fallback for old characters without history

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
    hp_level_history: list[int] = data["hp"].get("level_history", [])
    if len(hp_level_history) >= removed_level:
        hp_removed = hp_level_history.pop()
        data["hp"]["max"] = max(1, data["hp"]["max"] - hp_removed)
        data["hp"]["current"] = min(data["hp"]["current"], data["hp"]["max"])

    # Decrement the correct class entry
    cls_entry = next((c for c in basics["classes"] if c["class_index"] == cls_idx), None)
    if cls_entry:
        # Undo subclass if it was chosen at this class level
        cls_data = get_class(cls_idx)
        if cls_data and cls_entry["level"] == cls_data.get("subclass_level"):
            cls_entry["subclass"] = None
        cls_entry["level"] -= 1
        if cls_entry["level"] <= 0:
            basics["classes"] = [c for c in basics["classes"] if c["class_index"] != cls_idx]

    # Decrement total level
    new_level = removed_level - 1
    basics["level"] = new_level

    # Hit dice string — use primary class for simplified display
    primary_cls = get_class(primary_class(data))
    hit_die = primary_cls["hit_die"] if primary_cls else 8
    data["hit_dice"]["total"] = f"{new_level}d{hit_die}"

    return data
