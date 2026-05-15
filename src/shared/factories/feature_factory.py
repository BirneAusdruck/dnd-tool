from __future__ import annotations

from src.shared.domain.definitions.dice_value import DiceValue, FlatModifier
from src.shared.domain.definitions.effect_definition import EffectDefinition
from src.shared.domain.definitions.feature_definition import FeatureDefinition
from src.shared.domain.srd_constants import EffectCondition, EffectType


def _map_value(raw_value) -> FlatModifier | DiceValue | None:
    if isinstance(raw_value, int):
        return FlatModifier(value=raw_value)
    return None


class FeatureFactory:
    @classmethod
    def create(cls, raw: dict) -> FeatureDefinition:
        return FeatureDefinition(
            index=raw["index"],
            name=raw["name"],
            feature_type=raw.get("feat_type", "passive"),
            desc=raw["desc"],
            tags=tuple(raw.get("tags", [])),
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
            ),
        )