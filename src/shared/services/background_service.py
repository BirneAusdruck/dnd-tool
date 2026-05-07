from __future__ import annotations

from src.shared.repositories.srd_repository import SRDRepository, get_active_edition


class BackgroundService:
    _cache: dict[str, dict] = {}
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
    def get(cls, index: str) -> dict | None:
        cls._ensure_fresh()
        if index not in cls._cache:
            raw = SRDRepository().get_background(index)
            if raw is None:
                return None
            cls._cache[index] = raw
        return cls._cache[index]

    @classmethod
    def get_all(cls) -> list[dict]:
        cls._ensure_fresh()
        if not cls._all_loaded:
            for raw in SRDRepository().get_backgrounds():
                cls._cache[raw["index"]] = raw
            cls._all_loaded = True
        return list(cls._cache.values())

    @classmethod
    def invalidate(cls) -> None:
        cls._cache.clear()
        cls._all_loaded = False
        cls._cached_edition = ""
