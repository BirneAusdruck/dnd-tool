from __future__ import annotations

from src.shared.domain.definitions.dice_value import Damage, DiceValue, FlatModifier
from src.shared.domain.definitions.effect_definition import EffectDefinition
from src.shared.domain.definitions.item_definition import (
    ArmorDefinition, ContainerSlot, ItemContainer, ItemDefinition, ItemKind,
    MagicProperty, WeaponDefinition,
)
from src.shared.domain.srd_constants import (
    ArmorCategory, DamageType, DieType,
    EquipmentCategory, MagicItemCategory, MagicItemRarity,
    WeaponCategory, WeaponMastery, WeaponProperty,
)
from src.shared.factories.effect_factory import EffectFactory


def _map_container(raw: dict | None) -> ItemContainer:
    if raw is None:
        return ItemContainer(max_capacity=0, contents=())
    return ItemContainer(
        max_capacity=raw["max_capacity"],
        contents=tuple(
            ContainerSlot(
                qty=slot.get("qty", 1),
                index=slot.get("index"),
                desc=slot.get("desc"),
            )
            for slot in raw.get("contents", [])
        ),
    )


def _map_value(raw_value) -> FlatModifier | DiceValue | None:
    if isinstance(raw_value, int):
        return FlatModifier(value=raw_value)
    return None


def _map_effects(raw_list: list[dict]) -> tuple[EffectDefinition, ...]:
    return tuple(EffectFactory.create(e) for e in raw_list)


def _map_damage(raw: dict | None) -> Damage | None:
    if raw is None:
        return None
    return Damage(
        count=raw["count"],
        die=DieType(raw["die"]),
        damage_type=DamageType(raw["damage_type"]) if raw.get("damage_type") else DamageType.BLUDGEONING,
    )


class ItemFactory:
    @classmethod
    def create_weapon(cls, raw: dict) -> WeaponDefinition:
        damage = _map_damage(raw.get("damage"))
        range_raw = raw.get("range")
        weapon_range = tuple(range_raw) if range_raw else None
        mastery_raw = raw.get("mastery")
        magic = raw.get("magic")
        return WeaponDefinition(
            index=raw["index"],
            name=raw["name"],
            kind=ItemKind.MAGIC_ITEM if magic else ItemKind.WEAPON,
            category=MagicItemCategory.MAGIC_WEAPON if magic else WeaponCategory(raw["category"]),
            desc=raw.get("desc", ""),
            weight=raw.get("weight"),
            cost=raw.get("cost"),
            damage=damage,
            damage_versatile=_map_damage(raw.get("damage_versatile")),
            weapon_properties=tuple(
                WeaponProperty(p) for p in raw.get("properties", [])
            ),
            weapon_range=weapon_range,
            weapon_mastery=WeaponMastery(mastery_raw) if mastery_raw else None,
            magic=magic,
        )

    @classmethod
    def create_armor(cls, raw: dict) -> ArmorDefinition:
        magic = raw.get("magic")
        return ArmorDefinition(
            index=raw["index"],
            name=raw["name"],
            kind=ItemKind.MAGIC_ITEM if magic else ItemKind.ARMOR,
            category=MagicItemCategory.MAGIC_ARMOR if magic else ArmorCategory(raw["category"]),
            desc=raw.get("desc", ""),
            weight=raw.get("weight"),
            cost=raw.get("cost"),
            base_ac=raw["base_ac"],
            dex_bonus=raw.get("dex_bonus", False),
            max_dex=raw.get("max_dex"),
            str_requirement=raw.get("str_requirement", 0),
            stealth_disadvantage=raw.get("stealth_disadvantage", False),
            magic=magic,
        )

    @classmethod
    def create_equipment(cls, raw: dict) -> ItemDefinition:
        return ItemDefinition(
            index=raw["index"],
            name=raw["name"],
            kind=ItemKind.EQUIPMENT,
            category=EquipmentCategory(raw["category"]),
            desc=raw.get("desc", ""),
            weight=raw.get("weight"),
            cost=raw.get("cost"),
            effects=_map_effects(raw.get("effects_resolved", raw.get("effects", []))),
            container=_map_container(raw.get("container")),
        )

    @classmethod
    def create_magic_item(cls, raw: dict) -> ItemDefinition:
        attunement_raw = raw.get("attunement")
        return ItemDefinition(
            index=raw["index"],
            name=raw["name"],
            kind=ItemKind.MAGIC_ITEM,
            category=MagicItemCategory(raw["category"]),
            desc=raw.get("desc", ""),
            weight=raw.get("weight"),
            cost=raw.get("cost"),
            magic=MagicProperty(
                rarity=MagicItemRarity(raw["rarity"]),
                attunement=tuple(attunement_raw) if attunement_raw is not None else None,
                effects=_map_effects(raw.get("effects_resolved", raw.get("effects", []))),
            ),
        )
