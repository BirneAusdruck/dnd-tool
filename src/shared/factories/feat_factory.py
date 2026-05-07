from __future__ import annotations

from src.shared.domain.definitions.feat_definition import FeatDefinition


class FeatFactory:
    @classmethod
    def create(cls, raw: dict) -> FeatDefinition:
        return FeatDefinition(
            index=raw["index"],
            name=raw["name"],
            prerequisite=raw.get("prerequisite"),
            desc=raw.get("desc", ""),
            benefits=tuple(raw.get("benefits", [])),
        )
