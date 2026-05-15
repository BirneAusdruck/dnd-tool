from __future__ import annotations

from src.shared.domain.definitions.background_definition import BackgroundDefinition
from src.shared.factories.background_factory import BackgroundFactory
from src.shared.repositories.srd_repository import SRDRepository, get_active_edition


class BackgroundService:
    _cache: dict[str, dict] = {}
    _def_cache: dict[str, BackgroundDefinition] = {}
    _all_loaded: bool = False
    _all_defs_loaded: bool = False
    _cached_edition: str = ""

    @classmethod
    def _ensure_fresh(cls) -> None:
        current = get_active_edition()
        if cls._cached_edition != current:
            cls._cache.clear()
            cls._def_cache.clear()
            cls._all_loaded = False
            cls._all_defs_loaded = False
            cls._cached_edition = current

    # ── Raw dict access ────────────────────────────────────────────────────

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

    # ── Domain object access ───────────────────────────────────────────────

    @classmethod
    def get_definition(cls, index: str) -> BackgroundDefinition | None:
        cls._ensure_fresh()
        if index not in cls._def_cache:
            raw = SRDRepository().get_background(index)
            if raw is None:
                return None
            cls._def_cache[index] = BackgroundFactory.create(raw)
        return cls._def_cache[index]

    @classmethod
    def get_all_definitions(cls) -> list[BackgroundDefinition]:
        cls._ensure_fresh()
        if not cls._all_defs_loaded:
            for raw in SRDRepository().get_backgrounds():
                if raw["index"] not in cls._def_cache:
                    cls._def_cache[raw["index"]] = BackgroundFactory.create(raw)
            cls._all_defs_loaded = True
        return list(cls._def_cache.values())

    # ── Cache management ───────────────────────────────────────────────────

    @classmethod
    def invalidate(cls) -> None:
        cls._cache.clear()
        cls._def_cache.clear()
        cls._all_loaded = False
        cls._all_defs_loaded = False
        cls._cached_edition = ""
