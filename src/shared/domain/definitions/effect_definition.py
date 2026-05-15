from __future__ import annotations
from dataclasses import dataclass
from ..srd_constants import (
    EffectType, EffectRecipient, EffectCondition, DamageType, EffectTarget
)
from .dice_value import DiceValue, FlatModifier

@dataclass(frozen=True)
class EffectDefinition:
    index: str
    effect_type: EffectType
    target: EffectTarget
    value: FlatModifier | DiceValue | None = None
    condition: EffectCondition | None = None
    recipient: EffectRecipient | None = None
    is_complex: bool = False  # True = zu komplex für direkten Apply; Dispatch via index
    duration: int | None = None  # None = passiv/permanent, 0 = instantan, n = Sekunden
