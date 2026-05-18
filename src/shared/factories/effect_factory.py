from __future__ import annotations

from src.shared.domain.definitions.dice_value import DiceValue, FlatModifier
from src.shared.domain.definitions.effect_definition import (
    ComplexEffect, ConditionEffect, DamageEffect, EffectDefinition,
    HealEffect, LightEffect, MovementEffect, NarrativeEffect,
    ProficiencyEffect, ResistanceEffect, ResourceEffect,
    RollModifierEffect, SpellEffect, StatEffect,
)
from src.shared.domain.srd_constants import (
    Ability, AoEType, ChoiceType, Condition, DamageType,
    EffectCondition, EffectRecipient, EffectSourceCategory, EffectType,
    RefreshOn, SpellAttackType,
)

# Mapping effect_type → Subklasse
_SUBCLASS_MAP: dict[EffectType, type[EffectDefinition]] = {
    EffectType.STAT_BONUS:         StatEffect,
    EffectType.STAT_SET:           StatEffect,
    EffectType.AC_FORMULA:         StatEffect,
    EffectType.RESISTANCE:         ResistanceEffect,
    EffectType.IMMUNITY:           ResistanceEffect,
    EffectType.ADVANTAGE:          RollModifierEffect,
    EffectType.DISADVANTAGE:       RollModifierEffect,
    EffectType.RESOURCE:           ResourceEffect,
    EffectType.SPEED_BONUS:        MovementEffect,
    EffectType.SPEED_GRANT:        MovementEffect,
    EffectType.LIGHT_SOURCE:       LightEffect,
    EffectType.RESTORE_HP:         HealEffect,
    EffectType.STABILIZE:          HealEffect,
    EffectType.PROFICIENCY:        ProficiencyEffect,
    EffectType.DAMAGE_ON_TRIGGER:  DamageEffect,
    EffectType.AREA_HAZARD:        DamageEffect,
    EffectType.CONDITION_APPLY:    ConditionEffect,
    EffectType.SPELL_EFFECT:       SpellEffect,
    EffectType.NARRATIVE_FEATURE:  NarrativeEffect,
    EffectType.SPECIAL:            ComplexEffect,
}


def _map_flat_value(raw_value) -> FlatModifier | str | None:
    if isinstance(raw_value, int):
        return FlatModifier(value=raw_value)
    if isinstance(raw_value, str):
        return raw_value
    return None


def _opt(enum_cls, raw_key: str, raw: dict):
    val = raw.get(raw_key)
    return enum_cls(val) if val else None


class EffectFactory:
    @classmethod
    def create(cls, raw: dict) -> EffectDefinition:
        effect_type = EffectType(raw["effect_type"])
        subclass = _SUBCLASS_MAP.get(effect_type, ComplexEffect)

        base = dict(
            index=raw.get("index", ""),
            effect_type=effect_type,
            source_category=_opt(EffectSourceCategory, "source_category", raw),
            condition=_opt(EffectCondition, "condition", raw),
            recipient=_opt(EffectRecipient, "recipient", raw),
            duration=raw.get("duration"),
        )

        if subclass is StatEffect:
            return StatEffect(
                **base,
                target=raw.get("target", "special"),
                value=_map_flat_value(raw.get("value")),
                apply_if_lower=raw.get("apply_if_lower", False),
            )

        if subclass is RollModifierEffect:
            return RollModifierEffect(
                **base,
                target=raw.get("target", "special"),
                requires_choice=raw.get("requires_choice", False),
                choice_type=_opt(ChoiceType, "choice_type", raw),
            )

        if subclass is ResistanceEffect:
            return ResistanceEffect(
                **base,
                target=raw.get("target", "special"),
                requires_choice=raw.get("requires_choice", False),
                choice_type=_opt(ChoiceType, "choice_type", raw),
            )

        if subclass is MovementEffect:
            return MovementEffect(
                **base,
                target=raw.get("target", "speed"),
                value=_map_flat_value(raw.get("value")),
            )

        if subclass is ResourceEffect:
            return ResourceEffect(
                **base,
                target=raw.get("target", "special"),
                value=_map_flat_value(raw.get("value")),
                refresh_on=_opt(RefreshOn, "refresh_on", raw),
            )

        if subclass is LightEffect:
            return LightEffect(
                **base,
                bright=raw.get("value", 0) if isinstance(raw.get("value"), int) else 0,
                dim=raw.get("light_dim", 0) or 0,
            )

        if subclass is HealEffect:
            return HealEffect(
                **base,
                target=raw.get("target", "hp"),
                value=_map_flat_value(raw.get("value")),
            )

        if subclass is DamageEffect:
            raw_val = raw.get("value")
            dice_from_value = str(raw_val) if isinstance(raw_val, str) and "d" in raw_val else None
            # target ist DamageType nur bei damage_on_trigger, nicht bei area_hazard
            target_as_dtype = (
                _opt(DamageType, "target", raw)
                if effect_type == EffectType.DAMAGE_ON_TRIGGER else None
            )
            return DamageEffect(
                **base,
                target=raw.get("target", "special"),
                damage_dice=raw.get("damage_dice") or dice_from_value,
                damage_type=_opt(DamageType, "damage_type", raw) or target_as_dtype,
                save_dc=raw.get("save_dc"),
                save_stat=_opt(Ability, "save_stat", raw),
                save_half=raw.get("save_half", False),
            )

        if subclass is ProficiencyEffect:
            return ProficiencyEffect(
                **base,
                target=raw.get("target", "special"),
                requires_choice=raw.get("requires_choice", False),
                choice_type=_opt(ChoiceType, "choice_type", raw),
            )

        if subclass is ConditionEffect:
            return ConditionEffect(
                **base,
                target=raw.get("target", "special"),
                applied_condition=_opt(Condition, "applied_condition", raw),
                save_stat=_opt(Ability, "save_stat", raw),
                save_dc=raw.get("save_dc"),
            )

        if subclass is SpellEffect:
            return SpellEffect(
                **base,
                damage_dice=raw.get("damage_dice"),
                damage_type=_opt(DamageType, "damage_type", raw),
                heal_dice=raw.get("heal_dice"),
                applied_condition=_opt(Condition, "applied_condition", raw),
                save_stat=_opt(Ability, "save_stat", raw),
                save_dc_type=raw.get("save_dc_type", "spell_dc"),
                save_half=raw.get("save_half", False),
                aoe_type=_opt(AoEType, "aoe_type", raw),
                aoe_size=raw.get("aoe_size"),
                attack_type=_opt(SpellAttackType, "attack_type", raw),
                target_count=raw.get("target_count"),
                upcast_dice=raw.get("upcast_dice"),
                upcast_base=raw.get("upcast_base"),
                cantrip_scaling=raw.get("cantrip_scaling"),
            )

        if subclass is NarrativeEffect:
            return NarrativeEffect(**base)

        # ComplexEffect (SPECIAL oder Fallback)
        return ComplexEffect(
            **base,
            target=raw.get("target", "special"),
        )
