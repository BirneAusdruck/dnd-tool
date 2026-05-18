from __future__ import annotations

from src.shared.domain.definitions.effect_definition import EffectDefinition
from src.shared.domain.definitions.spell_definition import (
    MaterialComponent,
    SpellComponents,
    SpellDefinition,
)
from src.shared.domain.srd_constants import SpellSchool
from src.shared.factories.effect_factory import EffectFactory


def _map_material(raw: dict | None) -> MaterialComponent | None:
    if raw is None:
        return None
    return MaterialComponent(
        index=raw.get("index"),
        desc=raw.get("desc", ""),
        cost_gp=raw.get("cost_gp"),
        need_cost=raw.get("need_cost", False),
        consumed=raw.get("consumed", False),
    )


def _map_components(raw: dict) -> SpellComponents:
    return SpellComponents(
        verbal=raw.get("verbal", False),
        somatic=raw.get("somatic", False),
        material=_map_material(raw.get("material")),
    )


def _map_effects(raw_list: list[dict]) -> tuple[EffectDefinition, ...]:
    return tuple(EffectFactory.create(e) for e in raw_list)


class SpellFactory:
    @classmethod
    def create(cls, raw: dict) -> SpellDefinition:
        return SpellDefinition(
            index=raw["index"],
            name=raw["name"],
            level=raw["level"],
            school=SpellSchool(raw["school"]),
            casting_time=raw["casting_time"],
            range=raw.get("range", ""),
            components=_map_components(raw["components"]),
            concentration=raw.get("concentration", False),
            ritual=raw.get("ritual", False),
            classes=tuple(raw.get("classes", [])),
            effects=_map_effects(raw.get("effects_resolved", raw.get("effects", []))),
            desc=raw.get("desc", ""),
        )
