from __future__ import annotations

from src.shared.domain.definitions.class_definition import ClassDefinition
from src.shared.factories.class_factory import ClassFactory
from src.shared.repositories.srd_repository import SRDRepository, get_active_edition


class ClassService:
    _cache: dict[str, ClassDefinition] = {}
    _cached_edition: str = ""

    @classmethod
    def _ensure_fresh(cls) -> None:
        current = get_active_edition()
        if cls._cached_edition != current:
            cls._cache.clear()
            cls._cached_edition = current

    @classmethod
    def get(cls, index: str) -> ClassDefinition | None:
        cls._ensure_fresh()
        if index not in cls._cache:
            raw = SRDRepository().get_class(index)
            if raw is None:
                return None
            cls._cache[index] = ClassFactory.create(raw)
        return cls._cache[index]

    @classmethod
    def get_all(cls) -> list[ClassDefinition]:
        cls._ensure_fresh()
        repo = SRDRepository()
        for raw in repo.get_classes():
            idx = raw["index"]
            if idx not in cls._cache:
                cls._cache[idx] = ClassFactory.create(raw)
        return list(cls._cache.values())

    @classmethod
    def get_raw(cls, index: str) -> dict | None:
        return SRDRepository().get_class(index)

    @classmethod
    def get_all_raw(cls) -> list[dict]:
        return SRDRepository().get_classes()

    @classmethod
    def invalidate(cls) -> None:
        cls._cache.clear()
        cls._cached_edition = ""
