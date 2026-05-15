from __future__ import annotations
from dataclasses import dataclass, field
from .background_definition import AbilityBonus
from .effect_definition import EffectDefinition
from ..srd_constants import DamageType, ShortAbility, Size


@dataclass(frozen=True)
class RaceTrait:
    index: str
    name: str
    desc: str
    effects: tuple[EffectDefinition, ...]


@dataclass(frozen=True)
class AbilityBonusChoice:
    count: int          # how many different abilities to choose
    bonus: int          # bonus applied to each chosen ability
    note: str = ""


@dataclass(frozen=True)
class DraconicAncestryOption:
    dragon: str                 # e.g. "black", "red"
    damage_type: DamageType
    breath_shape: str           # e.g. "5x30 ft. line", "15 ft. cone"
    saving_throw: ShortAbility


@dataclass(frozen=True)
class SubraceDefinition:
    index: str
    name: str
    race_index: str
    ability_bonuses: tuple[AbilityBonus, ...]
    traits: tuple[RaceTrait, ...]


@dataclass(frozen=True)
class RaceDefinition:
    index: str
    name: str
    speed: int
    size: Size
    description: str
    ability_bonuses: tuple[AbilityBonus, ...]
    ability_bonus_choices: AbilityBonusChoice | None
    traits: tuple[RaceTrait, ...]
    languages: tuple[str, ...]
    subraces: tuple[SubraceDefinition, ...]
    draconic_ancestry: tuple[DraconicAncestryOption, ...] = field(default_factory=tuple)
