from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class ItemKind(str, Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    EQUIPMENT = "equipment"
    MAGIC_ITEM = "magic_item"


@dataclass(frozen=True)
class ItemDefinition:
    index: str
    name: str
    kind: ItemKind
    category: str
    desc: str
    weight: float | None
    cost: str | None

    # Weapon-specific
    damage: str | None = None
    damage_type: str | None = None
    damage_versatile: str | None = None
    weapon_properties: tuple[str, ...] = ()
    weapon_range: str | None = None

    # Armor-specific
    base_ac: int | None = None
    dex_bonus: bool = False
    max_dex: int | None = None
    str_requirement: int = 0
    stealth_disadvantage: bool = False

    # Magic item
    rarity: str | None = None
    requires_attunement: bool = False

    @property
    def is_weapon(self) -> bool:
        return self.kind == ItemKind.WEAPON

    @property
    def is_armor(self) -> bool:
        return self.kind == ItemKind.ARMOR

    @property
    def is_magic(self) -> bool:
        return self.kind == ItemKind.MAGIC_ITEM
