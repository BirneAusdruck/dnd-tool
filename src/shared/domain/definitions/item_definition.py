from __future__ import annotations
from dataclasses import dataclass, field
from .dice_value import Damage
from .effect_definition import EffectDefinition
from ..srd_constants import (
    ItemKind, ItemCategory, WeaponProperty, WeaponMastery, MagicItemRarity
)


@dataclass(frozen=True)
class EquipmentEntry:
    qty: int = 1
    index: str | None = None    # item index (equipment / weapons / armor JSON)
    desc: str | None = None     # narrative item with no game index
    choice: str | None = None   # category for "one type of X" selections
    gold: int | None = None     # starting gold in GP


@dataclass(frozen=True)
class ContainerSlot:
    qty: int = 1
    index: str | None = None    # item index if it has an SRD entry
    desc: str | None = None     # fallback for items with no SRD index


@dataclass(frozen=True)
class ItemContainer:
    max_capacity: int                       # theoretical maximum the container can hold
    contents: tuple[ContainerSlot, ...]     # default contents when the item is acquired


@dataclass(frozen=True)
class MagicProperty:
    rarity: MagicItemRarity
    attunement: tuple[str, ...] | None  # None = no attunement; ("any",) = any; ("paladin",) = specific class(es)
    effects: tuple[EffectDefinition, ...]


@dataclass(frozen=True)
class ItemDefinition:
    index: str
    name: str
    kind: ItemKind
    category: ItemCategory
    desc: str
    weight: float | None
    cost: int | None  # 10 CP = 1 SP, 100 CP = 1 GP, 1000 CP = 1 PP
    magic: MagicProperty | None = field(default=None, kw_only=True)
    effects: tuple[EffectDefinition, ...] = field(default_factory=tuple, kw_only=True)
    container: ItemContainer = field(default_factory=lambda: ItemContainer(max_capacity=0, contents=()), kw_only=True)

    def is_container(self) -> bool:
        return self.container.max_capacity > 0
    

@dataclass(frozen=True)
class WeaponDefinition(ItemDefinition):
    damage: Damage | None                        # None for special weapons like Net
    damage_versatile: Damage | None
    weapon_properties: tuple[WeaponProperty, ...]
    weapon_range: tuple[int, int] | None = None  # (normal, long)
    weapon_mastery: WeaponMastery | None = None


@dataclass(frozen=True)
class ArmorDefinition(ItemDefinition):
    base_ac: int
    dex_bonus: bool
    max_dex: int | None
    str_requirement: int | None
    stealth_disadvantage: bool
