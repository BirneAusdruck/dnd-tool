from __future__ import annotations

from src.shared.domain.definitions.race_definition import RaceDefinition, SubraceDefinition
from src.shared.factories.race_factory import RaceFactory
from src.shared.repositories.srd_repository import SRDRepository, get_active_edition


def _resolve_trait(raw_trait: dict, repo: SRDRepository) -> dict:
    """Return trait dict enriched with effects_resolved (inline effect dicts)."""
    resolved = []
    for eff_idx in raw_trait.get("effects", []):
        if isinstance(eff_idx, str):
            eff = repo.get_effect(eff_idx)
            if eff:
                resolved.append(eff)
        elif isinstance(eff_idx, dict):
            resolved.append(eff_idx)
    return {**raw_trait, "effects_resolved": resolved}


class RaceService:
    _cache: dict[str, RaceDefinition] = {}
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
    def _resolve(cls, raw: dict) -> RaceDefinition:
        repo = SRDRepository()
        # Resolve race traits
        traits_resolved = []
        for t_idx in raw.get("traits", []):
            t_raw = repo.get_trait(t_idx)
            if t_raw:
                traits_resolved.append(_resolve_trait(t_raw, repo))
        # Resolve subraces
        subraces_resolved = []
        for s_idx in raw.get("subraces", []):
            s_raw = repo.get_subrace_by_index(s_idx)
            if s_raw:
                s_traits = []
                for t_idx in s_raw.get("traits", []):
                    t_raw = repo.get_trait(t_idx)
                    if t_raw:
                        s_traits.append(_resolve_trait(t_raw, repo))
                subraces_resolved.append({**s_raw, "traits_resolved": s_traits})
        return RaceFactory.create({
            **raw,
            "traits_resolved": traits_resolved,
            "subraces_resolved": subraces_resolved,
        })

    @classmethod
    def get_definition(cls, index: str) -> RaceDefinition | None:
        cls._ensure_fresh()
        if index not in cls._cache:
            raw = SRDRepository().get_race(index)
            if raw is None:
                return None
            cls._cache[index] = cls._resolve(raw)
        return cls._cache[index]

    @classmethod
    def get_all_definitions(cls) -> list[RaceDefinition]:
        cls._ensure_fresh()
        if not cls._all_loaded:
            for raw in SRDRepository().get_races():
                cls._cache[raw["index"]] = cls._resolve(raw)
            cls._all_loaded = True
        return list(cls._cache.values())

    @classmethod
    def get_subrace(cls, race_index: str, subrace_index: str) -> SubraceDefinition | None:
        race = cls.get_definition(race_index)
        if not race:
            return None
        return next(
            (s for s in race.subraces if s.index == subrace_index), None
        )

    @classmethod
    def invalidate(cls) -> None:
        cls._cache.clear()
        cls._all_loaded = False
        cls._cached_edition = ""
