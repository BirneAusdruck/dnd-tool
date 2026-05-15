from __future__ import annotations

from src.shared.domain.definitions.dice_value import DiceValue, FlatModifier
from src.shared.domain.definitions.effect_definition import EffectDefinition
from src.shared.domain.definitions.feat_definition import (
    AbilityScorePrerequisite,
    FeatDefinition,
    FeatPrerequisite,
    LevelPrerequisite,
    Prerequisite,
    ProficiencyPrerequisite,
    SpellcastingPrerequisite,
)
from src.shared.domain.srd_constants import (
    Ability, ArmorProficiency, EffectCondition, EffectType,
    FeatTag, FeatType, WeaponCategory, WeaponProficiency,
)

_ARMOR_PROF_VALUES = {p.value for p in ArmorProficiency}
_WEAPON_CATEGORY_VALUES = {p.value for p in WeaponCategory}
_WEAPON_PROF_VALUES = {p.value for p in WeaponProficiency}


def _map_value(raw_value) -> FlatModifier | DiceValue | None:
    if isinstance(raw_value, int):
        return FlatModifier(value=raw_value)
    return None


def _map_prerequisite(raw: dict, mode: str) -> Prerequisite:
    kind = raw["type"]
    if kind == "ability_score":
        return AbilityScorePrerequisite(
            mode=mode,
            ability=Ability(raw["ability"]),
            min_value=raw["min_value"],
        )
    if kind == "proficiency":
        prof_val = raw["proficiency"]
        if prof_val in _ARMOR_PROF_VALUES:
            return ProficiencyPrerequisite(mode=mode, proficiency=ArmorProficiency(prof_val))
        if prof_val in _WEAPON_CATEGORY_VALUES:
            return ProficiencyPrerequisite(mode=mode, proficiency=WeaponCategory(prof_val))
        if prof_val in _WEAPON_PROF_VALUES:
            return ProficiencyPrerequisite(mode=mode, proficiency=WeaponProficiency(prof_val))
        return ProficiencyPrerequisite(mode=mode, proficiency=ArmorProficiency(prof_val))
    if kind == "feat":
        return FeatPrerequisite(mode=mode, feat_index=raw["feat_index"])
    if kind == "level":
        return LevelPrerequisite(mode=mode, min_value=raw["min_value"])
    if kind == "spellcasting":
        return SpellcastingPrerequisite(mode=mode)
    raise ValueError(f"Unknown prerequisite type: {kind!r}")


def _map_effects(raw_list: list[dict]) -> tuple[EffectDefinition, ...]:
    return tuple(
        EffectDefinition(
            index=e.get("index", ""),
            effect_type=EffectType(e["effect_type"]),
            target=e["target"],
            value=_map_value(e.get("value")),
            condition=EffectCondition(e["condition"]) if e.get("condition") else None,
            is_complex=e.get("is_complex", False),
                    duration=e.get("duration"),
        )
        for e in raw_list
    )


class FeatFactory:
    @classmethod
    def create(cls, raw: dict) -> FeatDefinition:
        mode = raw.get("prerequisites_mode", "all")
        return FeatDefinition(
            index=raw["index"],
            name=raw["name"],
            prerequisites=tuple(
                _map_prerequisite(p, mode) for p in raw.get("prerequisites", [])
            ),
            desc=raw.get("desc", ""),
            feat_type=FeatType(raw.get("feat_type", "passive")),
            tags=tuple(FeatTag(t) for t in raw.get("tags", [])),
            benefits=tuple(raw.get("benefits", [])),
            effects=_map_effects(raw.get("effects_resolved") or raw.get("effects") or []),
        )
