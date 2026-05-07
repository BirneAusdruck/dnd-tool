from __future__ import annotations

from src.shared.domain.definitions.class_definition import (
    ClassDefinition,
    SkillChoices,
    SpellcastingInfo,
)


class ClassFactory:
    @classmethod
    def create(cls, raw: dict) -> ClassDefinition:
        return ClassDefinition(
            index=raw["index"],
            name=raw["name"],
            hit_die=raw["hit_die"],
            primary_abilities=tuple(raw.get("primary_abilities", [])),
            saving_throws=tuple(raw.get("saving_throws", [])),
            armor_proficiencies=tuple(raw.get("armor_proficiencies", [])),
            weapon_proficiencies=tuple(raw.get("weapon_proficiencies", [])),
            tool_proficiencies=tuple(raw.get("tool_proficiencies", [])),
            skill_choices=cls._map_skill_choices(raw.get("skill_choices", {})),
            spellcasting=cls._map_spellcasting(raw.get("spellcasting")),
            subclass_name=raw.get("subclass_name", ""),
            subclass_level=raw.get("subclass_level", 0),
            subclasses=tuple(raw.get("subclasses", [])),
            features={
                int(lvl): tuple(feats)
                for lvl, feats in raw.get("features", {}).items()
            },
            starting_equipment_a=raw.get("starting_equipment_A", ""),
            starting_equipment_b=raw.get("starting_equipment_B", ""),
        )

    @staticmethod
    def _map_skill_choices(raw: dict) -> SkillChoices:
        return SkillChoices(
            count=raw.get("count", 0),
            options=tuple(raw.get("from", [])),
        )

    @staticmethod
    def _map_spellcasting(raw: dict | None) -> SpellcastingInfo | None:
        if not raw:
            return None
        raw_slots = raw.get("slots", [])
        raw_spells_known = raw.get("spells_known", [])
        return SpellcastingInfo(
            ability=raw.get("ability", ""),
            type=raw.get("type", ""),
            slots=tuple(tuple(row) for row in raw_slots),
            cantrips_known=tuple(raw.get("cantrips_known", [])),
            spells_known=tuple(raw_spells_known) if isinstance(raw_spells_known, list) else (),
        )
