from __future__ import annotations

from src.shared.domain.definitions.item_definition import ItemDefinition, ItemKind
from src.shared.factories.item_factory import ItemFactory
from src.shared.repositories.srd_repository import SRDRepository, get_active_edition


class ItemService:
    _cache: dict[str, ItemDefinition] = {}   # keyed by f"{kind}:{index}"
    _loaded: set[ItemKind] = set()
    _cached_edition: str = ""

    @classmethod
    def _ensure_fresh(cls) -> None:
        current = get_active_edition()
        if cls._cached_edition != current:
            cls._cache.clear()
            cls._loaded.clear()
            cls._cached_edition = current

    @classmethod
    def _key(cls, kind: ItemKind, index: str) -> str:
        return f"{kind.value}:{index}"

    # ── Weapons ────────────────────────────────────────────────────────────

    @classmethod
    def get_weapon(cls, index: str) -> ItemDefinition | None:
        cls._ensure_fresh()
        k = cls._key(ItemKind.WEAPON, index)
        if k not in cls._cache:
            raw = SRDRepository().get_weapon(index)
            if raw is None:
                return None
            cls._cache[k] = ItemFactory.create_weapon(raw)
        return cls._cache[k]

    @classmethod
    def get_all_weapons(cls) -> list[ItemDefinition]:
        cls._ensure_fresh()
        if ItemKind.WEAPON not in cls._loaded:
            for raw in SRDRepository().get_weapons():
                k = cls._key(ItemKind.WEAPON, raw["index"])
                if k not in cls._cache:
                    cls._cache[k] = ItemFactory.create_weapon(raw)
            cls._loaded.add(ItemKind.WEAPON)
        return [v for v in cls._cache.values() if v.kind == ItemKind.WEAPON]

    # ── Armor ──────────────────────────────────────────────────────────────

    @classmethod
    def get_armor(cls, index: str) -> ItemDefinition | None:
        cls._ensure_fresh()
        k = cls._key(ItemKind.ARMOR, index)
        if k not in cls._cache:
            raw = SRDRepository().get_armor(index)
            if raw is None:
                return None
            cls._cache[k] = ItemFactory.create_armor(raw)
        return cls._cache[k]

    @classmethod
    def get_all_armor(cls) -> list[ItemDefinition]:
        cls._ensure_fresh()
        if ItemKind.ARMOR not in cls._loaded:
            for raw in SRDRepository().get_armor_list():
                k = cls._key(ItemKind.ARMOR, raw["index"])
                if k not in cls._cache:
                    cls._cache[k] = ItemFactory.create_armor(raw)
            cls._loaded.add(ItemKind.ARMOR)
        return [v for v in cls._cache.values() if v.kind == ItemKind.ARMOR]

    # ── Equipment ──────────────────────────────────────────────────────────

    @classmethod
    def get_equipment(cls, index: str) -> ItemDefinition | None:
        cls._ensure_fresh()
        k = cls._key(ItemKind.EQUIPMENT, index)
        if k not in cls._cache:
            raw = SRDRepository().get_equipment(index)
            if raw is None:
                return None
            cls._cache[k] = ItemFactory.create_equipment(raw)
        return cls._cache[k]

    @classmethod
    def get_all_equipment(cls) -> list[ItemDefinition]:
        cls._ensure_fresh()
        if ItemKind.EQUIPMENT not in cls._loaded:
            for raw in SRDRepository().get_equipment_list():
                k = cls._key(ItemKind.EQUIPMENT, raw["index"])
                if k not in cls._cache:
                    cls._cache[k] = ItemFactory.create_equipment(raw)
            cls._loaded.add(ItemKind.EQUIPMENT)
        return [v for v in cls._cache.values() if v.kind == ItemKind.EQUIPMENT]

    # ── Magic Items ────────────────────────────────────────────────────────

    @classmethod
    def get_magic_item(cls, index: str) -> ItemDefinition | None:
        cls._ensure_fresh()
        k = cls._key(ItemKind.MAGIC_ITEM, index)
        if k not in cls._cache:
            raw = SRDRepository().get_magic_item(index)
            if raw is None:
                return None
            cls._cache[k] = ItemFactory.create_magic_item(raw)
        return cls._cache[k]

    @classmethod
    def get_all_magic_items(cls) -> list[ItemDefinition]:
        cls._ensure_fresh()
        if ItemKind.MAGIC_ITEM not in cls._loaded:
            for raw in SRDRepository().get_magic_items():
                k = cls._key(ItemKind.MAGIC_ITEM, raw["index"])
                if k not in cls._cache:
                    cls._cache[k] = ItemFactory.create_magic_item(raw)
            cls._loaded.add(ItemKind.MAGIC_ITEM)
        return [v for v in cls._cache.values() if v.kind == ItemKind.MAGIC_ITEM]

    # ── Raw dict access (for GUI display) ─────────────────────────────────

    @classmethod
    def get_weapon_raw(cls, index: str) -> dict | None:
        return SRDRepository().get_weapon(index)

    @classmethod
    def get_all_weapons_raw(cls) -> list[dict]:
        return SRDRepository().get_weapons()

    @classmethod
    def get_armor_raw(cls, index: str) -> dict | None:
        return SRDRepository().get_armor(index)

    @classmethod
    def get_all_armor_raw(cls) -> list[dict]:
        return SRDRepository().get_armor_list()

    @classmethod
    def get_equipment_raw(cls, index: str) -> dict | None:
        return SRDRepository().get_equipment(index)

    @classmethod
    def get_all_equipment_raw(cls) -> list[dict]:
        return SRDRepository().get_equipment_list()

    @classmethod
    def get_magic_item_raw(cls, index: str) -> dict | None:
        return SRDRepository().get_magic_item(index)

    @classmethod
    def get_all_magic_items_raw(cls) -> list[dict]:
        return SRDRepository().get_magic_items()

    # ── Cache management ───────────────────────────────────────────────────

    @classmethod
    def invalidate(cls) -> None:
        cls._cache.clear()
        cls._loaded.clear()
        cls._cached_edition = ""
