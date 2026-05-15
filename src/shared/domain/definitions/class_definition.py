from __future__ import annotations
from dataclasses import dataclass
from .feature_definition import FeatureDefinition
from ..srd_constants import (
    Skill, Ability, AbilitySavingThrow, SpellCastingType,
    DieType, ArmorProficiency, WeaponProficiencyAll,
)


@dataclass(frozen=True)
class SkillChoices:
    count: int
    options: tuple[Skill, ...]


@dataclass(frozen=True)
class SpellcastingInfo:
    ability: Ability
    type: SpellCastingType                    # "known" | "prepared" | "pact"
    slots: tuple[tuple[int, ...], ...]
    cantrips_known: tuple[int, ...]
    spells_known: tuple[int, ...]


@dataclass(frozen=True)
class SubclassEntry:
    index: str
    name: str


@dataclass(frozen=True)
class SubclassGroup:
    index: str
    name: str
    class_index: str
    subclasses: tuple[SubclassEntry, ...]


@dataclass(frozen=True)
class ClassStartingEquipment:
    index: str
    class_index: str
    option: str                               # "a" or "b"
    items: tuple                              # tuple[EquipmentEntry, ...]


@dataclass(frozen=True)
class ClassDefinition:
    index: str
    name: str
    hit_die: DieType
    primary_abilities: tuple[Ability, ...]
    saving_throws: tuple[AbilitySavingThrow, ...]
    armor_proficiencies: tuple[ArmorProficiency, ...]
    weapon_proficiencies: tuple[WeaponProficiencyAll, ...]
    tool_proficiencies: tuple[str, ...]
    skill_choices: SkillChoices
    spellcasting: SpellcastingInfo | None
    subclass_name: str                        # display name, kept for runtime compat
    subclass_level: int
    subclass_group_index: str                 # lazy ref → SubclassGroup in subclasses.json
    subclasses: tuple[str, ...]              # individual subclass indices
    features: dict[int, tuple[FeatureDefinition, ...]]
    starting_equipment_a_index: str           # lazy ref → ClassStartingEquipment
    starting_equipment_b_index: str           # lazy ref → ClassStartingEquipment

    def features_at(self, level: int) -> tuple[FeatureDefinition, ...]:
        return self.features.get(level, ())

    def features_up_to(self, level: int) -> list[FeatureDefinition]:
        result: list[FeatureDefinition] = []
        for lvl in range(1, level + 1):
            result.extend(self.features.get(lvl, ()))
        return result

    def spell_slots_at(self, class_level: int) -> tuple[int, ...]:
        if not self.spellcasting:
            return ()
        idx = min(class_level - 1, len(self.spellcasting.slots) - 1)
        return self.spellcasting.slots[idx]

    def asi_levels(self) -> frozenset[int]:
        return frozenset(
            lvl for lvl, feats in self.features.items()
            if any("Ability Score Improvement" in f.name for f in feats)
        )
