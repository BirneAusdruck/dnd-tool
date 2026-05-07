from __future__ import annotations

from src.shared.repositories.srd_repository import SRDRepository, get_active_edition


class RaceService:
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
            raw = SRDRepository().get_race(index)
            if raw is None:
                return None
            cls._cache[index] = raw
        return cls._cache[index]

    @classmethod
    def get_all(cls) -> list[dict]:
        cls._ensure_fresh()
        if not cls._all_loaded:
            for raw in SRDRepository().get_races():
                cls._cache[raw["index"]] = raw
            cls._all_loaded = True
        return list(cls._cache.values())

    @classmethod
    def get_subrace(cls, race_index: str, subrace_index: str) -> dict | None:
        race = cls.get(race_index)
        if not race:
            return None
        return next(
            (s for s in race.get("subraces", []) if s["index"] == subrace_index), None
        )

    @classmethod
    def invalidate(cls) -> None:
        cls._cache.clear()
        cls._all_loaded = False
        cls._cached_edition = ""
