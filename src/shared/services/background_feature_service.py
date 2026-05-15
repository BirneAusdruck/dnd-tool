from __future__ import annotations

from src.shared.domain.definitions.background_definition import BackgroundFeature
from src.shared.factories.background_factory import BackgroundFactory
from src.shared.repositories.srd_repository import SRDRepository, get_active_edition


def _resolve_effects(raw: dict) -> dict:
    effects_raw = raw.get("effects")
    if not effects_raw:
        return {**raw, "effects_resolved": []}
    repo = SRDRepository()
    resolved = []
    for eff_item in effects_raw:
        if isinstance(eff_item, str):
            eff = repo.get_effect(eff_item)
            if eff:
                resolved.append(eff)
        elif isinstance(eff_item, dict):
            resolved.append(eff_item)
    return {**raw, "effects_resolved": resolved}


class BackgroundFeatureService:
    _cache: dict[str, BackgroundFeature] = {}
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
        for raw in SRDRepository().get_background_features():
            idx = raw["index"]
            if idx not in cls._cache:
                cls._cache[idx] = BackgroundFactory.create_feature(_resolve_effects(raw))
        cls._all_loaded = True

    @classmethod
    def get_definition(cls, index: str) -> BackgroundFeature | None:
        cls._ensure_fresh()
        if index not in cls._cache:
            raw = SRDRepository().get_background_feature(index)
            if raw is None:
                return None
            cls._cache[index] = BackgroundFactory.create_feature(_resolve_effects(raw))
        return cls._cache[index]

    @classmethod
    def get_all_definitions(cls) -> list[BackgroundFeature]:
        cls._ensure_fresh()
        cls._load_all()
        return list(cls._cache.values())

    @classmethod
    def invalidate(cls) -> None:
        cls._cache.clear()
        cls._all_loaded = False
        cls._cached_edition = ""
