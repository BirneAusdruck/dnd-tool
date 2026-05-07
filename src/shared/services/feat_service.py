from __future__ import annotations

from src.shared.domain.definitions.feat_definition import FeatDefinition
from src.shared.factories.feat_factory import FeatFactory
from src.shared.repositories.srd_repository import SRDRepository, get_active_edition


class FeatService:
    _cache: dict[str, FeatDefinition] = {}
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
        for raw in SRDRepository().get_feats():
            idx = raw["index"]
            if idx not in cls._cache:
                cls._cache[idx] = FeatFactory.create(raw)
        cls._all_loaded = True

    @classmethod
    def get(cls, index: str) -> FeatDefinition | None:
        cls._ensure_fresh()
        if index not in cls._cache:
            raw = SRDRepository().get_feat(index)
            if raw is None:
                return None
            cls._cache[index] = FeatFactory.create(raw)
        return cls._cache[index]

    @classmethod
    def get_all(cls) -> list[FeatDefinition]:
        cls._ensure_fresh()
        cls._load_all()
        return sorted(cls._cache.values(), key=lambda f: f.name)

    @classmethod
    def get_raw(cls, index: str) -> dict | None:
        return SRDRepository().get_feat(index)

    @classmethod
    def get_all_raw(cls) -> list[dict]:
        return SRDRepository().get_feats()

    @classmethod
    def invalidate(cls) -> None:
        cls._cache.clear()
        cls._all_loaded = False
        cls._cached_edition = ""
