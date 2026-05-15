from __future__ import annotations
from dataclasses import dataclass
from .feature_definition import FeatureDefinition

@dataclass(frozen=True)
class SubclassDefinition:
    index: str
    name: str
    parent_class: str # index der Elternklasse
    flavor: str       # "Primal Path", "Martial Archetype", "Sacred Oath"...
    desc: str
    features: dict[int, tuple[FeatureDefinition, ...]]
    subclass_spells: tuple[tuple[int, str], ...] | None # (level, spell_index) für Domain/Oath Spells

    def features_at(self, level: int) -> tuple[FeatureDefinition, ...]:
        return self.features.get(level, ())

    def features_up_to(self, level: int) -> list[FeatureDefinition]:
        result: list[FeatureDefinition] = []
        for lvl in range(1, level + 1):
            result.extend(self.features.get(lvl, ()))
        return result