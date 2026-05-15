from __future__ import annotations

from src.shared.domain.definitions.class_definition import SubclassGroup
from src.shared.factories.class_factory import ClassFactory
from src.shared.repositories.srd_repository import SRDRepository, get_active_edition


class SubclassService:
    _cache: dict[str, SubclassGroup] = {}
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
        for raw in SRDRepository().get_subclass_groups():
            idx = raw["index"]
            if idx not in cls._cache:
                cls._cache[idx] = ClassFactory.create_subclass_group(raw)
        cls._all_loaded = True

    @classmethod
    def get_definition(cls, index: str) -> SubclassGroup | None:
        cls._ensure_fresh()
        if index not in cls._cache:
            raw = SRDRepository().get_subclass_group(index)
            if raw is None:
                return None
            cls._cache[index] = ClassFactory.create_subclass_group(raw)
        return cls._cache[index]

    @classmethod
    def get_for_class(cls, class_index: str) -> SubclassGroup | None:
        cls._ensure_fresh()
        cls._load_all()
        return next((g for g in cls._cache.values() if g.class_index == class_index), None)

    @classmethod
    def get_all_definitions(cls) -> list[SubclassGroup]:
        cls._ensure_fresh()
        cls._load_all()
        return list(cls._cache.values())

    @classmethod
    def invalidate(cls) -> None:
        cls._cache.clear()
        cls._all_loaded = False
        cls._cached_edition = ""
