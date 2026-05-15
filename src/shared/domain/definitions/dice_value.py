from __future__ import annotations
from dataclasses import dataclass
from ..srd_constants import (
    DieType, DamageType, Stat
    )

@dataclass(frozen=True)
class DiceValue:  # abstrakt, nie direkt instanzieren
    count: int
    die: DieType

@dataclass(frozen=True)
class Damage(DiceValue):
    damage_type: DamageType

@dataclass(frozen=True)
class Heal(DiceValue):
    stat_target: Stat

@dataclass(frozen=True)
class Buff(DiceValue):
    stat_target: Stat
    exceeds_cap: bool = False

@dataclass(frozen=True)
class Debuff(DiceValue):
    stat_target: Stat


@dataclass(frozen=True)
class FlatModifier:  # abstrakt, kein Würfelanteil; target kommt aus EffectDefinition
    value: int

@dataclass(frozen=True)
class FeatBonus(FlatModifier):
    exceeds_cap: bool = False  # True = ignoriert Attribut-Cap (z.B. STR max 20)

@dataclass(frozen=True)
class RaceBonus(FlatModifier):
    pass