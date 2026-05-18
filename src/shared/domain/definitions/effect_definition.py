from __future__ import annotations
from dataclasses import dataclass
from ..srd_constants import (
    Ability, AoEType, ChoiceType, Condition, DamageType,
    EffectCondition, EffectRecipient, EffectSourceCategory, EffectType,
    RefreshOn, SpellAttackType,
)
from .dice_value import DiceValue, FlatModifier


@dataclass(frozen=True)
class EffectDefinition:
    """Basisklasse für alle Effekt-Definitionen. Statisches Informationspaket für spätere Logik."""
    index: str
    effect_type: EffectType
    source_category: EffectSourceCategory | None = None
    condition: EffectCondition | None = None      # wann der Effekt aktiv ist
    recipient: EffectRecipient | None = None
    duration: int | None = None                   # None=permanent, 0=instant, n=Sekunden


# ---------------------------------------------------------------------------
# Stat-Effekte: stat_bonus | stat_set | ac_formula
# ---------------------------------------------------------------------------

@dataclass(frozen=True, kw_only=True)
class StatEffect(EffectDefinition):
    target: str = "special"
    value: FlatModifier | DiceValue | str | None = None
    apply_if_lower: bool = False          # stat_set: nur wenn aktueller Wert < Zielwert


# ---------------------------------------------------------------------------
# Würfelmodifikatoren: advantage | disadvantage
# ---------------------------------------------------------------------------

@dataclass(frozen=True, kw_only=True)
class RollModifierEffect(EffectDefinition):
    target: str = "special"
    requires_choice: bool = False
    choice_type: ChoiceType | None = None


# ---------------------------------------------------------------------------
# Resistenz / Immunität: resistance | immunity
# ---------------------------------------------------------------------------

@dataclass(frozen=True, kw_only=True)
class ResistanceEffect(EffectDefinition):
    target: str = "special"
    requires_choice: bool = False
    choice_type: ChoiceType | None = None


# ---------------------------------------------------------------------------
# Bewegung: speed_bonus | speed_grant
# ---------------------------------------------------------------------------

@dataclass(frozen=True, kw_only=True)
class MovementEffect(EffectDefinition):
    target: str = "speed"
    value: FlatModifier | str | None = None       # int, "double", "equal_to_walk"


# ---------------------------------------------------------------------------
# Ressourcen: resource
# ---------------------------------------------------------------------------

@dataclass(frozen=True, kw_only=True)
class ResourceEffect(EffectDefinition):
    target: str = "special"
    value: FlatModifier | str | None = None       # int oder "CHA_mod"
    refresh_on: RefreshOn | None = None


# ---------------------------------------------------------------------------
# Lichtquelle: light_source
# ---------------------------------------------------------------------------

@dataclass(frozen=True, kw_only=True)
class LightEffect(EffectDefinition):
    bright: int = 0
    dim: int = 0


# ---------------------------------------------------------------------------
# Heilung / Stabilisierung: restore_hp | stabilize
# ---------------------------------------------------------------------------

@dataclass(frozen=True, kw_only=True)
class HealEffect(EffectDefinition):
    target: str = "hp"
    value: FlatModifier | str | None = None       # int oder Würfelformel


# ---------------------------------------------------------------------------
# Schaden bei Auslöser: damage_on_trigger | area_hazard
# ---------------------------------------------------------------------------

@dataclass(frozen=True, kw_only=True)
class DamageEffect(EffectDefinition):
    target: str = "special"
    damage_dice: str | None = None                # "1d4", "2d6"
    damage_type: DamageType | None = None
    save_dc: int | None = None
    save_stat: Ability | None = None
    save_half: bool = False


# ---------------------------------------------------------------------------
# Proficiency: proficiency
# ---------------------------------------------------------------------------

@dataclass(frozen=True, kw_only=True)
class ProficiencyEffect(EffectDefinition):
    target: str = "special"
    requires_choice: bool = False
    choice_type: ChoiceType | None = None


# ---------------------------------------------------------------------------
# Zustand anwenden: condition_apply
# ---------------------------------------------------------------------------

@dataclass(frozen=True, kw_only=True)
class ConditionEffect(EffectDefinition):
    target: str = "special"
    applied_condition: Condition | None = None
    save_stat: Ability | None = None
    save_dc: int | str | None = None              # int oder "spell_dc"


# ---------------------------------------------------------------------------
# Spell-Mechanik: spell_effect
# Vollständige strukturierte Beschreibung eines Zaubereffekts.
# ---------------------------------------------------------------------------

@dataclass(frozen=True, kw_only=True)
class SpellEffect(EffectDefinition):
    damage_dice: str | None = None                # "2d6", "8d6"
    damage_type: DamageType | None = None
    heal_dice: str | None = None                  # "1d8", "4d4+4"
    applied_condition: Condition | None = None
    save_stat: Ability | None = None
    save_dc_type: str = "spell_dc"                # "spell_dc" | "fixed"
    save_half: bool = False                       # halber Schaden bei Erfolg
    aoe_type: AoEType | None = None
    aoe_size: int | None = None                   # Radius/Länge in Fuß
    attack_type: SpellAttackType | None = None
    target_count: int | str | None = None         # 1, "all_in_aoe", etc.
    upcast_dice: str | None = None                # "+ X Würfel pro Slot über Basis"
    upcast_base: int | None = None                # Slot-Level ab dem Upcast greift
    cantrip_scaling: str | None = None            # "+Xd bei Level 5/11/17"


# ---------------------------------------------------------------------------
# Narrative Feature: narrative_feature
# Reines Fluff ohne Mechanik (Background-Features, Rollenspiel-Boni).
# ---------------------------------------------------------------------------

@dataclass(frozen=True, kw_only=True)
class NarrativeEffect(EffectDefinition):
    pass


# ---------------------------------------------------------------------------
# Komplex: special
# System-Dispatch via index; keine Felder ausdrückbar.
# ---------------------------------------------------------------------------

@dataclass(frozen=True, kw_only=True)
class ComplexEffect(EffectDefinition):
    target: str = "special"
