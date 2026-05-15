from __future__ import annotations

from src.shared.domain.definitions.background_definition import BackgroundTraitGroup


class BackgroundTraitGroupFactory:
    @classmethod
    def create(cls, raw: dict) -> BackgroundTraitGroup:
        return BackgroundTraitGroup(
            index=raw["index"],
            desc=tuple(raw.get("desc", [])),
        )
