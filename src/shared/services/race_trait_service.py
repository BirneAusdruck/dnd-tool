from __future__ import annotations

from src.shared.domain.definitions.race_definition import RaceTrait
from src.shared.factories.race_factory import _map_effect, _map_trait
from src.shared.repositories.srd_repository import SRDRepository, get_active_edition


class RaceTraitService:
    _cache: dict[str, RaceTrait] = {}
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
    def _resolve(cls, raw: dict) -> RaceTrait:
        repo = SRDRepository()
        effects_resolved = []
        for eff_idx in raw.get("effects", []):
            if isinstance(eff_idx, str):
                eff = repo.get_effect(eff_idx)
                if eff:
                    effects_resolved.append(eff)
            elif isinstance(eff_idx, dict):
                effects_resolved.append(eff_idx)
        return _map_trait({**raw, "effects_resolved": effects_resolved})

    @classmethod
    def get_definition(cls, index: str) -> RaceTrait | None:
        cls._ensure_fresh()
        if index not in cls._cache:
            raw = SRDRepository().get_trait(index)
            if raw is None:
                return None
            cls._cache[index] = cls._resolve(raw)
        return cls._cache[index]

    @classmethod
    def get_all_definitions(cls) -> list[RaceTrait]:
        cls._ensure_fresh()
        if not cls._all_loaded:
            for raw in SRDRepository().get_traits():
                idx = raw["index"]
                if idx not in cls._cache:
                    cls._cache[idx] = cls._resolve(raw)
            cls._all_loaded = True
        return list(cls._cache.values())

    @classmethod
    def invalidate(cls) -> None:
        cls._cache.clear()
        cls._all_loaded = False
        cls._cached_edition = ""
