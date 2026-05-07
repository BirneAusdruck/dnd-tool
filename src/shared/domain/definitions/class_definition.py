from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SkillChoices:
    count: int
    options: tuple[str, ...]


@dataclass(frozen=True)
class SpellcastingInfo:
    ability: str
    type: str                    # "known" | "prepared" | "pact"
    slots: tuple[tuple[int, ...], ...]
    cantrips_known: tuple[int, ...]
    spells_known: tuple[int, ...]


@dataclass(frozen=True)
class ClassDefinition:
    index: str
    name: str
    hit_die: int
    primary_abilities: tuple[str, ...]
    saving_throws: tuple[str, ...]
    armor_proficiencies: tuple[str, ...]
    weapon_proficiencies: tuple[str, ...]
    tool_proficiencies: tuple[str, ...]
    skill_choices: SkillChoices
    spellcasting: SpellcastingInfo | None
    subclass_name: str
    subclass_level: int
    subclasses: tuple[str, ...]
    features: dict[int, tuple[str, ...]]   # level → feature names
    starting_equipment_a: str
    starting_equipment_b: str

    def features_at(self, level: int) -> tuple[str, ...]:
        return self.features.get(level, ())

    def features_up_to(self, level: int) -> list[str]:
        result: list[str] = []
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
            if any("Ability Score Improvement" in f for f in feats)
        )
