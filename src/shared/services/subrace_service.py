from __future__ import annotations

from src.shared.domain.definitions.race_definition import SubraceDefinition
from src.shared.factories.race_factory import _map_subrace, _map_trait
from src.shared.repositories.srd_repository import SRDRepository, get_active_edition


class SubraceService:
    _cache: dict[str, SubraceDefinition] = {}
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
    def _resolve(cls, raw: dict) -> SubraceDefinition:
        repo = SRDRepository()
        traits_resolved = []
        for t_idx in raw.get("traits", []):
            t_raw = repo.get_trait(t_idx)
            if t_raw:
                effects_resolved = []
                for eff_idx in t_raw.get("effects", []):
                    if isinstance(eff_idx, str):
                        eff = repo.get_effect(eff_idx)
                        if eff:
                            effects_resolved.append(eff)
                    elif isinstance(eff_idx, dict):
                        effects_resolved.append(eff_idx)
                traits_resolved.append({**t_raw, "effects_resolved": effects_resolved})
        return _map_subrace({**raw, "traits_resolved": traits_resolved})

    @classmethod
    def get_definition(cls, index: str) -> SubraceDefinition | None:
        cls._ensure_fresh()
        if index not in cls._cache:
            raw = SRDRepository().get_subrace_by_index(index)
            if raw is None:
                return None
            cls._cache[index] = cls._resolve(raw)
        return cls._cache[index]

    @classmethod
    def get_all_definitions(cls) -> list[SubraceDefinition]:
        cls._ensure_fresh()
        if not cls._all_loaded:
            for raw in SRDRepository().get_subraces_list():
                idx = raw["index"]
                if idx not in cls._cache:
                    cls._cache[idx] = cls._resolve(raw)
            cls._all_loaded = True
        return list(cls._cache.values())

    @classmethod
    def get_for_race(cls, race_index: str) -> list[SubraceDefinition]:
        cls.get_all_definitions()
        return [s for s in cls._cache.values() if s.race_index == race_index]

    @classmethod
    def invalidate(cls) -> None:
        cls._cache.clear()
        cls._all_loaded = False
        cls._cached_edition = ""
