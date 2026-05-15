from __future__ import annotations
from dataclasses import dataclass
from .effect_definition import EffectDefinition
from ..srd_constants import (
    SpellSchool
)

_LEVEL_ORDINALS = ("1st", "2nd", "3rd") + tuple(f"{i}th" for i in range(4, 10))

@dataclass(frozen=True)
class MaterialComponent:
    index: str | None # lazy reference auf ItemDefinition.Index sofern ein Item referenziert wird
    desc: str
    cost_gp: int | None # kein spezifischer wert
    need_cost: bool # sagt aus ob ein gegenstand mindestens einen wert haben muss
    consumed: bool

@dataclass(frozen=True)
class SpellComponents:
    verbal: bool
    somatic: bool
    material: MaterialComponent | None # None = kein Material nötig

@dataclass(frozen=True)
class SpellDefinition:
    index: str
    name: str
    level: int
    school: SpellSchool
    casting_time: int # in sekunden denn 6sec = 1round
    range: str
    components: SpellComponents
    concentration: bool
    ritual: bool
    classes: tuple[str, ...] # lazy reference auf ClassDefinition.index
    effects: tuple[EffectDefinition, ...]
    desc: str

    @property
    def is_cantrip(self) -> bool:
        return self.level == 0

    @property
    def level_name(self) -> str:
        if self.level == 0:
            return "Cantrip"
        return f"{_LEVEL_ORDINALS[self.level - 1]}-level"

    def available_to(self, class_index: str) -> bool:
        return class_index in self.classes
