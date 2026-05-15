from __future__ import annotations

from src.shared.domain.definitions.dice_value import DiceValue, FlatModifier
from src.shared.domain.definitions.effect_definition import EffectDefinition
from src.shared.domain.srd_constants import EffectCondition, EffectType


def _map_value(raw_value) -> FlatModifier | DiceValue | None:
    if isinstance(raw_value, int):
        return FlatModifier(value=raw_value)
    return None


class EffectFactory:
    @classmethod
    def create(cls, raw: dict) -> EffectDefinition:
        return EffectDefinition(
            index=raw.get("index", ""),
            effect_type=EffectType(raw["effect_type"]),
            target=raw["target"],
            value=_map_value(raw.get("value")),
            condition=EffectCondition(raw["condition"]) if raw.get("condition") else None,
            is_complex=raw.get("is_complex", False),
            duration=raw.get("duration"),
        )