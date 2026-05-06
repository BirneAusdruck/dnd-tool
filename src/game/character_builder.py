"""
Stateless helper functions for DnD 5e character math.
All functions take raw character data dicts and return derived values.
"""

from __future__ import annotations
from src.game.srd_loader import get_race, get_subrace, get_class, SKILLS

STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]

POINT_BUY_COSTS = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}
POINT_BUY_BUDGET = 27


# ── Ability Score Math ─────────────────────────────────────────────────────

def modifier(score: int) -> int:
    return (score - 10) // 2


def proficiency_bonus(level: int) -> int:
    return (level - 1) // 4 + 2


def passive_perception(wis_score: int, perception_proficient: bool, level: int) -> int:
    base = 10 + modifier(wis_score)
    if perception_proficient:
        base += proficiency_bonus(level)
    return base


def skill_bonus(ability_score: int, proficient: bool, level: int, expertise: bool = False) -> int:
    bonus = modifier(ability_score)
    prof = proficiency_bonus(level)
    if expertise:
        bonus += prof * 2
    elif proficient:
        bonus += prof
    return bonus


# ── HP ─────────────────────────────────────────────────────────────────────

def max_hp_at_level_1(class_index: str, con_score: int) -> int:
    cls = get_class(class_index)
    if not cls:
        return 4 + modifier(con_score)
    return cls["hit_die"] + modifier(con_score)


# ── AC ─────────────────────────────────────────────────────────────────────

ARMOR_TABLE = {
    "Padded":      {"base": 11, "type": "light",  "dex": "full"},
    "Leather":     {"base": 11, "type": "light",  "dex": "full"},
    "Studded Leather": {"base": 12, "type": "light", "dex": "full"},
    "Hide":        {"base": 12, "type": "medium", "dex": 2},
    "Chain Shirt": {"base": 13, "type": "medium", "dex": 2},
    "Scale Mail":  {"base": 14, "type": "medium", "dex": 2},
    "Breastplate": {"base": 14, "type": "medium", "dex": 2},
    "Half Plate":  {"base": 15, "type": "medium", "dex": 2},
    "Ring Mail":   {"base": 14, "type": "heavy",  "dex": 0},
    "Chain Mail":  {"base": 16, "type": "heavy",  "dex": 0},
    "Splint":      {"base": 17, "type": "heavy",  "dex": 0},
    "Plate":       {"base": 18, "type": "heavy",  "dex": 0},
}


def calc_ac(
    armor_name: str | None,
    dex_score: int,
    has_shield: bool,
    class_index: str,
    str_score: int = 10,
    wis_score: int = 10,
    con_score: int = 10,
) -> int:
    dex_mod = modifier(dex_score)
    shield_bonus = 2 if has_shield else 0

    if armor_name and armor_name in ARMOR_TABLE:
        armor = ARMOR_TABLE[armor_name]
        if armor["dex"] == "full":
            return armor["base"] + dex_mod + shield_bonus
        else:
            return armor["base"] + min(dex_mod, armor["dex"]) + shield_bonus

    # Unarmored defense
    if class_index == "barbarian":
        return 10 + dex_mod + modifier(con_score) + shield_bonus
    if class_index == "monk":
        return 10 + dex_mod + modifier(wis_score)

    return 10 + dex_mod + shield_bonus


# ── Racial Ability Bonuses ─────────────────────────────────────────────────

def apply_racial_bonuses(
    base_scores: dict[str, int],
    race_index: str,
    subrace_index: str | None = None,
    choice_scores: list[str] | None = None,
) -> dict[str, int]:
    scores = dict(base_scores)
    race = get_race(race_index)
    if not race:
        return scores

    for bonus in race.get("ability_bonuses", []):
        ab = bonus["score"]
        if ab in ("choice_1", "choice_2"):
            continue
        if ab in scores:
            scores[ab] += bonus["bonus"]

    # Half-elf: player picks two extra scores
    if choice_scores:
        for ab in choice_scores:
            if ab in scores:
                scores[ab] += 1

    if subrace_index:
        subrace = get_subrace(race_index, subrace_index)
        if subrace:
            for bonus in subrace.get("ability_bonuses", []):
                if bonus["score"] in scores:
                    scores[bonus["score"]] += bonus["bonus"]

    return scores


# ── Skill Proficiencies ────────────────────────────────────────────────────

def collect_proficiencies(
    class_index: str,
    background_index: str,
    chosen_skills: list[str],
    race_index: str,
) -> set[str]:
    from src.game.srd_loader import get_background

    profs: set[str] = set(chosen_skills)

    bg = get_background(background_index)
    if bg:
        profs.update(bg.get("skill_proficiencies", []))

    race = get_race(race_index)
    if race:
        for trait in race.get("traits", []):
            if "Perception" in trait.get("name", "") and "Keen" in trait.get("name", ""):
                profs.add("Perception")
            if "Intimidation" in trait.get("name", "") and "Menacing" in trait.get("name", ""):
                profs.add("Intimidation")

    return profs


# ── Full Character Sheet Data Builder ─────────────────────────────────────

def build_character_data(
    name: str,
    edition: str,
    race_index: str,
    subrace_index: str | None,
    class_index: str,
    background_index: str,
    alignment: str,
    base_ability_scores: dict[str, int],
    chosen_skills: list[str],
    chosen_cantrips: list[str] | None = None,
    chosen_spells: list[str] | None = None,
    half_elf_score_choices: list[str] | None = None,
    dragonborn_ancestry: str | None = None,
    personality: str = "",
    ideals: str = "",
    bonds: str = "",
    flaws: str = "",
    notes: str = "",
) -> dict:
    final_scores = apply_racial_bonuses(
        base_ability_scores, race_index, subrace_index, half_elf_score_choices
    )
    cls = get_class(class_index)
    hit_die = cls["hit_die"] if cls else 8
    saving_throws = cls["saving_throws"] if cls else []
    armor_profs = cls["armor_proficiencies"] if cls else []
    weapon_profs = cls["weapon_proficiencies"] if cls else []

    skill_profs = list(collect_proficiencies(class_index, background_index, chosen_skills, race_index))

    level1_hp = max_hp_at_level_1(class_index, final_scores.get("CON", 10))

    return {
        "meta": {"edition": edition, "version": "0.1"},
        "basics": {
            "name": name,
            "race": race_index,
            "subrace": subrace_index,
            "class": class_index,
            "subclass": None,
            "background": background_index,
            "alignment": alignment,
            "level": 1,
            "experience": 0,
            "dragonborn_ancestry": dragonborn_ancestry,
            # Multiclassing-ready: each entry is {class_index, level, subclass}
            "classes": [{"class_index": class_index, "level": 1, "subclass": None}],
            # History of ASI choices: [{total_level, class_index, changes}]
            "asi_history": [],
            # Feats currently held and their acquisition history
            "feats": [],
            "feat_history": [],
        },
        "ability_scores": final_scores,
        "hp": {
            "max": level1_hp,
            "current": level1_hp,
            "temp": 0,
            # Per-level HP gains; index 0 = level 1, subsequent = gains per level-up
            "level_history": [level1_hp],
        },
        "hit_dice": {"total": f"1d{hit_die}", "used": 0},
        "death_saves": {"successes": 0, "failures": 0},
        "proficiencies": {
            "skills": skill_profs,
            "saving_throws": saving_throws,
            "armor": armor_profs,
            "weapons": weapon_profs,
            "tools": [],
            "languages": [],
        },
        "equipment": {
            "armor": None,
            "shield": False,
            "weapons": [],
            "inventory": [],
            "currency": {"cp": 0, "sp": 0, "ep": 0, "gp": 0, "pp": 0},
        },
        "spellcasting": {
            "cantrips": chosen_cantrips or [],
            "spells_known": chosen_spells or [],
            "spell_slots_used": [],
        } if cls and cls.get("spellcasting") else None,
        "traits": {
            "personality": personality,
            "ideals": ideals,
            "bonds": bonds,
            "flaws": flaws,
        },
        "conditions": [],
        "notes": notes,
    }


# ── Derived Values (for display) ───────────────────────────────────────────

def derive_sheet_values(data: dict) -> dict:
    scores = data["ability_scores"]
    level = data["basics"]["level"]
    profs = data["proficiencies"]
    prof_bonus = proficiency_bonus(level)

    skill_values = {}
    for skill in SKILLS:
        ab_score = scores.get(skill["ability"], 10)
        proficient = skill["name"] in profs.get("skills", [])
        skill_values[skill["name"]] = skill_bonus(ab_score, proficient, level)

    save_values = {}
    for ab in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
        score = scores.get(ab, 10)
        proficient = ab in profs.get("saving_throws", [])
        save_values[ab] = modifier(score) + (prof_bonus if proficient else 0)

    return {
        "ability_modifiers": {ab: modifier(scores.get(ab, 10)) for ab in ["STR","DEX","CON","INT","WIS","CHA"]},
        "proficiency_bonus": prof_bonus,
        "saving_throws": save_values,
        "skills": skill_values,
        "passive_perception": passive_perception(
            scores.get("WIS", 10), "Perception" in profs.get("skills", []), level
        ),
        "initiative": modifier(scores.get("DEX", 10)),
    }
