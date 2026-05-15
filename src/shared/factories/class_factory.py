from __future__ import annotations

from src.shared.domain.definitions.class_definition import (
    ClassDefinition,
    ClassStartingEquipment,
    SkillChoices,
    SpellcastingInfo,
    SubclassEntry,
    SubclassGroup,
)
from src.shared.domain.definitions.dice_value import DiceValue, FlatModifier
from src.shared.domain.definitions.effect_definition import EffectDefinition
from src.shared.domain.definitions.feature_definition import FeatureDefinition
from src.shared.domain.definitions.item_definition import EquipmentEntry
from src.shared.domain.srd_constants import (
    Ability, AbilitySavingThrow, ArmorProficiency, DieType,
    EffectCondition, EffectType, FeatureTag, FeatureType,
    Skill, SpellCastingType, WeaponCategory, WeaponProficiency,
)

def _map_value(raw_value) -> FlatModifier | DiceValue | None:
    if isinstance(raw_value, int):
        return FlatModifier(value=raw_value)
    return None


_WEAPON_PROF_MAP: dict[str, list[str]] = {
    "simple":  ["simple_melee", "simple_ranged"],
    "martial": ["martial_melee", "martial_ranged"],
}

_SINGLE_WEAPON_MAP: dict[str, str] = {
    "clubs": "club", "daggers": "dagger", "maces": "mace",
    "sickles": "sickle", "javelins": "javelin", "spears": "spear",
    "quarterstaffs": "quarterstaff", "slings": "sling", "darts": "dart",
    "light crossbows": "crossbow_light", "shortswords": "shortsword",
    "scimitars": "scimitar", "longswords": "longsword",
    "club": "club", "dagger": "dagger", "mace": "mace",
    "sickle": "sickle", "javelin": "javelin", "spear": "spear",
    "quarterstaff": "quarterstaff", "sling": "sling", "dart": "dart",
    "light crossbow": "crossbow_light", "shortsword": "shortsword",
    "scimitar": "scimitar", "longsword": "longsword",
    "rapier": "rapier", "hand crossbow": "crossbow_hand",
    "heavy crossbow": "crossbow_heavy", "longbow": "longbow",
    "handaxe": "handaxe", "light hammer": "light_hammer",
    "greatclub": "greatclub", "greataxe": "greataxe",
    "greatsword": "greatsword",
}

_ARMOR_MAP: dict[str, str] = {
    "light": "light", "medium": "medium", "heavy": "heavy",
    "shields": "shield", "shields (non-metal)": "shield",
}

_TOOL_MAP: dict[str, str] = {
    "herbalism kit": "herbalism_kit",
    "thieves' tools": "thieves_tools",
    "three musical instruments of your choice": "instrument_choice_3",
    "one artisan's tool or musical instrument": "artisans_or_instrument_choice",
}

_ABILITY_SHORT_TO_LONG: dict[str, str] = {
    "STR": "strength", "DEX": "dexterity", "CON": "constitution",
    "INT": "intelligence", "WIS": "wisdom", "CHA": "charisma",
}


def _parse_weapon_profs(raw_list: list[str]) -> tuple:
    result: list = []
    for raw in raw_list:
        key = raw.lower().strip()
        if key in _WEAPON_PROF_MAP:
            result.extend(WeaponCategory(v) for v in _WEAPON_PROF_MAP[key])
        elif key in _SINGLE_WEAPON_MAP:
            result.append(WeaponProficiency(_SINGLE_WEAPON_MAP[key]))
    return tuple(result)


def _parse_skill_choices_from(raw) -> tuple[Skill, ...]:
    if not isinstance(raw, list):
        return ()
    return tuple(Skill(s) for s in raw if isinstance(s, str) and s in Skill._value2member_map_)


def _parse_equipment(raw_list: list[dict]) -> tuple[EquipmentEntry, ...]:
    return tuple(
        EquipmentEntry(
            qty=e.get("qty", 1),
            index=e.get("index"),
            desc=e.get("desc"),
            choice=e.get("choice"),
            gold=e.get("gold"),
        )
        for e in raw_list
    )


class ClassFactory:
    @classmethod
    def create(cls, raw: dict) -> ClassDefinition:
        hit_die_raw = raw["hit_die"]
        hit_die = DieType(hit_die_raw) if isinstance(hit_die_raw, str) else DieType(f"d{hit_die_raw}")

        return ClassDefinition(
            index=raw["index"],
            name=raw["name"],
            hit_die=hit_die,
            primary_abilities=tuple(
                Ability(_ABILITY_SHORT_TO_LONG.get(a, a))
                for a in raw.get("primary_abilities", [])
            ),
            saving_throws=tuple(
                AbilitySavingThrow(f"{s}_saving_throw") if "_saving_throw" not in s else AbilitySavingThrow(s)
                for s in raw.get("saving_throws", [])
            ),
            armor_proficiencies=tuple(
                ArmorProficiency(_ARMOR_MAP.get(a.lower().strip(), a.lower().strip()))
                for a in raw.get("armor_proficiencies", [])
            ),
            weapon_proficiencies=_parse_weapon_profs(raw.get("weapon_proficiencies", [])),
            tool_proficiencies=tuple(
                _TOOL_MAP.get(t.lower().strip(), t.lower().strip())
                for t in raw.get("tool_proficiencies", [])
            ),
            skill_choices=cls._map_skill_choices(raw.get("skill_choices", {})),
            spellcasting=cls._map_spellcasting(raw.get("spellcasting")),
            subclass_name=raw.get("subclass_name", ""),
            subclass_level=raw.get("subclass_level", 0),
            subclass_group_index=raw.get("subclass_group_index", ""),
            subclasses=tuple(raw.get("subclasses", [])),
            features={
                int(lvl): tuple(cls._map_feature(f) for f in feats)
                for lvl, feats in raw.get("features_resolved", raw.get("features", {})).items()
                if isinstance(feats, list) and feats and isinstance(feats[0], dict)
            },
            starting_equipment_a_index=raw.get("starting_equipment_a_index", ""),
            starting_equipment_b_index=raw.get("starting_equipment_b_index", ""),
        )

    @classmethod
    def create_subclass_group(cls, raw: dict) -> SubclassGroup:
        return SubclassGroup(
            index=raw["index"],
            name=raw["name"],
            class_index=raw.get("class", ""),
            subclasses=tuple(
                SubclassEntry(index=s["index"], name=s["name"])
                for s in raw.get("subclasses", [])
            ),
        )

    @classmethod
    def create_starting_equipment(cls, raw: dict) -> ClassStartingEquipment:
        return ClassStartingEquipment(
            index=raw["index"],
            class_index=raw.get("class", ""),
            option=raw.get("option", "a"),
            items=_parse_equipment(raw.get("items", [])),
        )

    @staticmethod
    def _map_feature(raw: dict) -> FeatureDefinition:
        return FeatureDefinition(
            index=raw["index"],
            name=raw["name"],
            desc=raw.get("desc", ""),
            feature_type=FeatureType(raw.get("feature_type", "passive")),
            tags=tuple(FeatureTag(t) for t in raw.get("tags", [])),
            effects=tuple(
                EffectDefinition(
                    index=e.get("index", ""),
                    effect_type=EffectType(e["effect_type"]),
                    target=e["target"],
                    value=_map_value(e.get("value")),
                    condition=EffectCondition(e["condition"]) if e.get("condition") else None,
                    is_complex=e.get("is_complex", False),
                    duration=e.get("duration"),
                )
                for e in raw.get("effects", [])
                if isinstance(e, dict)
            ),
            benefits=tuple(raw.get("benefits", [])),
        )

    @staticmethod
    def _map_skill_choices(raw: dict) -> SkillChoices:
        return SkillChoices(
            count=raw.get("count", 0),
            options=_parse_skill_choices_from(raw.get("from", [])),
        )

    @staticmethod
    def _map_spellcasting(raw: dict | None) -> SpellcastingInfo | None:
        if not raw:
            return None
        ability_raw = raw.get("ability", "")
        ability = Ability(_ABILITY_SHORT_TO_LONG.get(ability_raw, ability_raw))
        raw_slots = raw.get("slots", [])
        raw_spells_known = raw.get("spells_known", [])
        return SpellcastingInfo(
            ability=ability,
            type=SpellCastingType(raw.get("type", "prepared")),
            slots=tuple(tuple(row) for row in raw_slots),
            cantrips_known=tuple(raw.get("cantrips_known", [])),
            spells_known=tuple(raw_spells_known) if isinstance(raw_spells_known, list) else (),
        )
