from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class FeatDefinition:
    index: str
    name: str
    prerequisite: str | None
    desc: str
    benefits: tuple[str, ...]

    def has_prerequisite(self) -> bool:
        return self.prerequisite is not None
