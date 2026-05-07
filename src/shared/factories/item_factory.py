from __future__ import annotations

from src.shared.domain.definitions.item_definition import ItemDefinition, ItemKind


class ItemFactory:
    @classmethod
    def create_weapon(cls, raw: dict) -> ItemDefinition:
        return ItemDefinition(
            index=raw["index"],
            name=raw["name"],
            kind=ItemKind.WEAPON,
            category=raw.get("category", ""),
            desc=raw.get("desc", ""),
            weight=raw.get("weight"),
            cost=raw.get("cost"),
            damage=raw.get("damage"),
            damage_type=raw.get("damage_type"),
            damage_versatile=raw.get("damage_versatile"),
            weapon_properties=tuple(raw.get("properties", [])),
            weapon_range=raw.get("range"),
        )

    @classmethod
    def create_armor(cls, raw: dict) -> ItemDefinition:
        return ItemDefinition(
            index=raw["index"],
            name=raw["name"],
            kind=ItemKind.ARMOR,
            category=raw.get("category", ""),
            desc=raw.get("desc", ""),
            weight=raw.get("weight"),
            cost=raw.get("cost"),
            base_ac=raw.get("base_ac"),
            dex_bonus=raw.get("dex_bonus", False),
            max_dex=raw.get("max_dex"),
            str_requirement=raw.get("str_requirement", 0),
            stealth_disadvantage=raw.get("stealth_disadvantage", False),
        )

    @classmethod
    def create_equipment(cls, raw: dict) -> ItemDefinition:
        return ItemDefinition(
            index=raw["index"],
            name=raw["name"],
            kind=ItemKind.EQUIPMENT,
            category=raw.get("category", ""),
            desc=raw.get("desc", ""),
            weight=raw.get("weight"),
            cost=raw.get("cost"),
        )

    @classmethod
    def create_magic_item(cls, raw: dict) -> ItemDefinition:
        return ItemDefinition(
            index=raw["index"],
            name=raw["name"],
            kind=ItemKind.MAGIC_ITEM,
            category=raw.get("category", ""),
            desc=raw.get("desc", ""),
            weight=raw.get("weight"),
            cost=raw.get("cost"),
            rarity=raw.get("rarity"),
            requires_attunement=raw.get("attunement", False),
        )
