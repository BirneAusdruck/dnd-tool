from __future__ import annotations

from src.shared.domain.definitions.background_definition import BackgroundTraitGroup
from src.shared.factories.background_trait_factory import BackgroundTraitGroupFactory
from src.shared.repositories.srd_repository import SRDRepository, get_active_edition


class _TraitGroupService:
    """Base for background trait-group services (bonds, flaws, ideals, personality traits)."""

    _fetch: str  # repo method name: "get_background_bonds" etc.
    _fetch_one: str  # repo method name: "get_background_bond" etc.
    _cache: dict[str, list[BackgroundTraitGroup]] = {}
    _cached_edition: str = ""

    @classmethod
    def _ensure_fresh(cls) -> None:
        current = get_active_edition()
        if cls._cached_edition != current:
            cls._cache.clear()
            cls._cached_edition = current

    @classmethod
    def _all(cls) -> list[BackgroundTraitGroup]:
        cls._ensure_fresh()
        if cls._cached_edition not in cls._cache:
            repo = SRDRepository()
            raw_list: list[dict] = getattr(repo, cls._fetch)()
            cls._cache[cls._cached_edition] = [
                BackgroundTraitGroupFactory.create(r) for r in raw_list
            ]
        return cls._cache[cls._cached_edition]

    @classmethod
    def get_all(cls) -> list[BackgroundTraitGroup]:
        return list(cls._all())

    @classmethod
    def get(cls, group_index: str) -> BackgroundTraitGroup | None:
        return next((g for g in cls._all() if g.index == group_index), None)

    @classmethod
    def resolve(cls, group_indices: tuple[str, ...] | list[str]) -> list[str]:
        """Flatten desc lists of multiple groups into a single list of strings."""
        result: list[str] = []
        for idx in group_indices:
            group = cls.get(idx)
            if group:
                result.extend(group.desc)
        return result

    @classmethod
    def invalidate(cls) -> None:
        cls._cache.clear()
        cls._cached_edition = ""


class BackgroundPersonalityTraitService(_TraitGroupService):
    _fetch = "get_background_personality_traits"
    _fetch_one = "get_background_personality_trait"
    _cache: dict[str, list[BackgroundTraitGroup]] = {}
    _cached_edition: str = ""


class BackgroundIdealService(_TraitGroupService):
    _fetch = "get_background_ideals"
    _fetch_one = "get_background_ideal"
    _cache: dict[str, list[BackgroundTraitGroup]] = {}
    _cached_edition: str = ""


class BackgroundBondService(_TraitGroupService):
    _fetch = "get_background_bonds"
    _fetch_one = "get_background_bond"
    _cache: dict[str, list[BackgroundTraitGroup]] = {}
    _cached_edition: str = ""


class BackgroundFlawService(_TraitGroupService):
    _fetch = "get_background_flaws"
    _fetch_one = "get_background_flaw"
    _cache: dict[str, list[BackgroundTraitGroup]] = {}
    _cached_edition: str = ""
