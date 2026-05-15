from __future__ import annotations

from src.shared.domain.definitions.background_definition import AbilityBonus
from src.shared.domain.definitions.dice_value import DiceValue, FlatModifier
from src.shared.domain.definitions.effect_definition import EffectDefinition
from src.shared.domain.definitions.race_definition import (
    AbilityBonusChoice,
    DraconicAncestryOption,
    RaceDefinition,
    RaceTrait,
    SubraceDefinition,
)
from src.shared.domain.srd_constants import (
    DamageType, EffectCondition, EffectType, ShortAbility, Size,
)


def _map_value(raw_value) -> FlatModifier | DiceValue | None:
    if isinstance(raw_value, int):
        return FlatModifier(value=raw_value)
    return None


def _map_effect(raw: dict) -> EffectDefinition:
    return EffectDefinition(
        index=raw.get("index", ""),
        effect_type=EffectType(raw["effect_type"]),
        target=raw["target"],
        value=_map_value(raw.get("value")),
        condition=EffectCondition(raw["condition"]) if raw.get("condition") else None,
        is_complex=raw.get("is_complex", False),
        duration=raw.get("duration"),
    )


def _map_trait(raw: dict) -> RaceTrait:
    return RaceTrait(
        index=raw["index"],
        name=raw["name"],
        desc=raw["desc"],
        effects=tuple(_map_effect(e) for e in raw.get("effects_resolved", raw.get("effects", []))),
    )


def _map_ability_bonuses(raw_list: list[dict]) -> tuple[AbilityBonus, ...]:
    return tuple(
        AbilityBonus(score=ShortAbility(b["score"]), bonus=b["bonus"])
        for b in raw_list
        if not b["score"].startswith("choice_")
    )


def _map_draconic_ancestry(raw_list: list[dict]) -> tuple[DraconicAncestryOption, ...]:
    return tuple(
        DraconicAncestryOption(
            dragon=e["dragon"],
            damage_type=DamageType(e["damage_type"]),
            breath_shape=e["breath_shape"],
            saving_throw=ShortAbility(e["saving_throw"]),
        )
        for e in raw_list
    )


def _map_subrace(raw: dict) -> SubraceDefinition:
    return SubraceDefinition(
        index=raw["index"],
        name=raw["name"],
        race_index=raw.get("race", ""),
        ability_bonuses=_map_ability_bonuses(raw.get("ability_bonuses", [])),
        traits=tuple(_map_trait(t) for t in raw.get("traits_resolved", raw.get("traits", []))),
    )


class RaceFactory:
    @classmethod
    def create(cls, raw: dict) -> RaceDefinition:
        raw_choices = raw.get("ability_bonus_choices")
        ability_bonus_choices = (
            AbilityBonusChoice(
                count=raw_choices["count"],
                bonus=raw_choices["bonus"],
                note=raw_choices.get("note", ""),
            )
            if raw_choices
            else None
        )
        return RaceDefinition(
            index=raw["index"],
            name=raw["name"],
            speed=raw["speed"],
            size=Size(raw["size"]),
            description=raw.get("description", ""),
            ability_bonuses=_map_ability_bonuses(raw.get("ability_bonuses", [])),
            ability_bonus_choices=ability_bonus_choices,
            traits=tuple(_map_trait(t) for t in raw.get("traits_resolved", [])),
            languages=tuple(raw.get("languages", [])),
            subraces=tuple(_map_subrace(s) for s in raw.get("subraces_resolved", [])),
            draconic_ancestry=_map_draconic_ancestry(raw.get("draconic_ancestry", [])),
        )
