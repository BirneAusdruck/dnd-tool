from __future__ import annotations
from dataclasses import dataclass, field
from .effect_definition import EffectDefinition
from ..srd_constants import (
    FeatType, FeatTag, Ability, ArmorProficiency, WeaponProficiencyAll, ToolProficiency
)


@dataclass(frozen=True)
class Prerequisite:
    mode: str  # "all" (AND) | "any" (OR)


@dataclass(frozen=True)
class AbilityScorePrerequisite(Prerequisite):
    ability: Ability
    min_value: int


@dataclass(frozen=True)
class ProficiencyPrerequisite(Prerequisite):
    proficiency: ArmorProficiency | WeaponProficiencyAll | ToolProficiency


@dataclass(frozen=True)
class FeatPrerequisite(Prerequisite):
    feat_index: str


@dataclass(frozen=True)
class LevelPrerequisite(Prerequisite):
    min_value: int


@dataclass(frozen=True)
class SpellcastingPrerequisite(Prerequisite):
    pass


@dataclass(frozen=True)
class FeatDefinition:
    index: str
    name: str
    prerequisites: tuple[Prerequisite, ...]  # empty = no prerequisites
    desc: str
    feat_type: FeatType
    tags: tuple[FeatTag, ...]
    benefits: tuple[str, ...]
    effects: tuple[EffectDefinition, ...]

    def has_prerequisite(self) -> bool:
        return bool(self.prerequisites)
