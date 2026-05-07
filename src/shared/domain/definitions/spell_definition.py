from __future__ import annotations
from dataclasses import dataclass

_LEVEL_ORDINALS = ["1st", "2nd", "3rd"] + [f"{i}th" for i in range(4, 10)]


@dataclass(frozen=True)
class SpellDefinition:
    name: str
    level: int
    school: str
    casting_time: str
    range: str
    components: str
    duration: str
    classes: tuple[str, ...]
    desc: str

    @property
    def is_cantrip(self) -> bool:
        return self.level == 0

    @property
    def level_name(self) -> str:
        if self.level == 0:
            return "Cantrip"
        return f"{_LEVEL_ORDINALS[self.level - 1]}-level"

    def available_to(self, class_index: str) -> bool:
        return class_index in self.classes
