from __future__ import annotations
from dataclasses import dataclass, field
from .effect_definition import EffectDefinition
from .item_definition import EquipmentEntry
from ..srd_constants import Skill, ShortAbility


@dataclass(frozen=True)
class BackgroundTraitGroup:
    index: str
    desc: tuple[str, ...]


@dataclass(frozen=True)
class BackgroundFeature:
    index: str
    name: str
    desc: str
    effects: tuple[EffectDefinition, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class BackgroundEquipmentSet:
    index: str
    items: tuple[EquipmentEntry, ...]


@dataclass(frozen=True)
class AbilityBonus:
    score: ShortAbility
    bonus: int


@dataclass(frozen=True)
class BackgroundDefinition:
    index: str
    name: str
    skill_proficiencies: tuple[Skill, ...]
    tool_proficiencies: tuple[str, ...]
    languages: int
    equipment_index: str                        # lazy ref → BackgroundEquipmentSet
    feature_index: str                          # lazy ref → BackgroundFeature
    personality_trait_groups: tuple[str, ...]   # lazy refs → BackgroundTraitGroup (personality traits)
    ideal_groups: tuple[str, ...]               # lazy refs → BackgroundTraitGroup (ideals)
    bond_groups: tuple[str, ...]                # lazy refs → BackgroundTraitGroup (bonds)
    flaw_groups: tuple[str, ...]                # lazy refs → BackgroundTraitGroup (flaws)
    ability_bonuses: tuple[AbilityBonus, ...] = field(default_factory=tuple)
    origin_feat_index: str | None = None        # lazy ref → FeatDefinition; None in 5.1
