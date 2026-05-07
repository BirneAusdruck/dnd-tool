from __future__ import annotations

from src.shared.domain.definitions.spell_definition import SpellDefinition


class SpellFactory:
    @classmethod
    def create(cls, raw: dict) -> SpellDefinition:
        return SpellDefinition(
            name=raw["name"],
            level=raw["level"],
            school=raw.get("school", ""),
            casting_time=raw.get("casting_time", ""),
            range=raw.get("range", ""),
            components=raw.get("components", ""),
            duration=raw.get("duration", ""),
            classes=tuple(raw.get("classes", [])),
            desc=raw.get("desc", ""),
        )
