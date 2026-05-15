from __future__ import annotations
from dataclasses import dataclass, field
from .effect_definition import EffectDefinition
from ..srd_constants import (
    FeatureType, FeatureTag
)

@dataclass(frozen=True)
class FeatureDefinition:
    index: str
    name: str
    desc: str
    feature_type: FeatureType
    tags: tuple[FeatureTag, ...]
    effects: tuple[EffectDefinition, ...]
    benefits: tuple[str, ...] = field(default_factory=tuple)
