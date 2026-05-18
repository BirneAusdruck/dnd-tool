from __future__ import annotations

from src.shared.domain.definitions.background_definition import (
    AbilityBonus, BackgroundDefinition, BackgroundEquipmentSet, BackgroundFeature,
)
from src.shared.domain.definitions.effect_definition import EffectDefinition
from src.shared.domain.definitions.item_definition import EquipmentEntry
from src.shared.domain.srd_constants import Skill, ShortAbility
from src.shared.factories.effect_factory import EffectFactory


def _map_effects(raw_list: list[dict]) -> tuple[EffectDefinition, ...]:
    return tuple(EffectFactory.create(e) for e in raw_list if isinstance(e, dict))


class BackgroundFactory:
    @classmethod
    def create(cls, raw: dict) -> BackgroundDefinition:
        return BackgroundDefinition(
            index=raw["index"],
            name=raw["name"],
            skill_proficiencies=tuple(Skill(s) for s in raw.get("skill_proficiencies", [])),
            tool_proficiencies=tuple(raw.get("tool_proficiencies", [])),
            languages=raw.get("languages", 0),
            equipment_index=raw["equipment_index"],
            feature_index=raw["feature_index"],
            personality_trait_groups=tuple(raw.get("personality_traits", [])),
            ideal_groups=tuple(raw.get("ideals", [])),
            bond_groups=tuple(raw.get("bonds", [])),
            flaw_groups=tuple(raw.get("flaws", [])),
            ability_bonuses=tuple(
                AbilityBonus(score=ShortAbility(b["score"]), bonus=b["bonus"])
                for b in raw.get("ability_bonuses", [])
            ),
            origin_feat_index=raw.get("origin_feat_index"),
        )

    @classmethod
    def create_feature(cls, raw: dict) -> BackgroundFeature:
        return BackgroundFeature(
            index=raw["index"],
            name=raw["name"],
            desc=raw.get("desc", ""),
            effects=_map_effects(raw.get("effects_resolved", raw.get("effects", []))),
        )

    @classmethod
    def create_equipment_set(cls, raw: dict) -> BackgroundEquipmentSet:
        return BackgroundEquipmentSet(
            index=raw["index"],
            items=tuple(
                EquipmentEntry(
                    qty=e.get("qty", 1),
                    index=e.get("index"),
                    desc=e.get("desc"),
                    choice=e.get("choice"),
                    gold=e.get("gold"),
                )
                for e in raw.get("items", [])
            ),
        )
