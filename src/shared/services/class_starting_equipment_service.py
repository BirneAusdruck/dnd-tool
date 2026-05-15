from __future__ import annotations

from src.shared.domain.definitions.class_definition import ClassStartingEquipment
from src.shared.factories.class_factory import ClassFactory
from src.shared.repositories.srd_repository import SRDRepository, get_active_edition


class ClassStartingEquipmentService:
    _cache: dict[str, ClassStartingEquipment] = {}
    _all_loaded: bool = False
    _cached_edition: str = ""

    @classmethod
    def _ensure_fresh(cls) -> None:
        current = get_active_edition()
        if cls._cached_edition != current:
            cls._cache.clear()
            cls._all_loaded = False
            cls._cached_edition = current

    @classmethod
    def _load_all(cls) -> None:
        if cls._all_loaded:
            return
        for raw in SRDRepository().get_class_starting_equipments():
            idx = raw["index"]
            if idx not in cls._cache:
                cls._cache[idx] = ClassFactory.create_starting_equipment(raw)
        cls._all_loaded = True

    @classmethod
    def get_definition(cls, index: str) -> ClassStartingEquipment | None:
        cls._ensure_fresh()
        if index not in cls._cache:
            raw = SRDRepository().get_class_starting_equipment(index)
            if raw is None:
                return None
            cls._cache[index] = ClassFactory.create_starting_equipment(raw)
        return cls._cache[index]

    @classmethod
    def get_all_definitions(cls) -> list[ClassStartingEquipment]:
        cls._ensure_fresh()
        cls._load_all()
        return list(cls._cache.values())

    @classmethod
    def invalidate(cls) -> None:
        cls._cache.clear()
        cls._all_loaded = False
        cls._cached_edition = ""
