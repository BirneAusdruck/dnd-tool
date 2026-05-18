from __future__ import annotations

from src.shared.domain.definitions.effect_definition import EffectDefinition
from src.shared.domain.definitions.feature_definition import FeatureDefinition
from src.shared.factories.effect_factory import EffectFactory


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
                EffectFactory.create(e)
                for e in raw.get("effects", [])
            ),
        )