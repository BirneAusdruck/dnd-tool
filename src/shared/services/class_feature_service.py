from __future__ import annotations

from src.shared.domain.definitions.feature_definition import FeatureDefinition
from src.shared.factories.class_factory import ClassFactory
from src.shared.repositories.srd_repository import SRDRepository, get_active_edition


class ClassFeatureService:
    _cache: dict[str, FeatureDefinition] = {}
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
    def _resolve_feature(cls, raw: dict) -> FeatureDefinition:
        """Load effects from effects.json and build FeatureDefinition."""
        repo = SRDRepository()
        effects_raw = []
        for eff_idx in raw.get("effects", []):
            if isinstance(eff_idx, str):
                eff = repo.get_effect(eff_idx)
                if eff:
                    effects_raw.append(eff)
            elif isinstance(eff_idx, dict):
                effects_raw.append(eff_idx)
        return ClassFactory._map_feature({**raw, "effects": effects_raw})

    @classmethod
    def _load_all(cls) -> None:
        if cls._all_loaded:
            return
        for raw in SRDRepository().get_features():
            idx = raw["index"]
            if idx not in cls._cache:
                cls._cache[idx] = cls._resolve_feature(raw)
        cls._all_loaded = True

    @classmethod
    def get_definition(cls, index: str) -> FeatureDefinition | None:
        cls._ensure_fresh()
        if index not in cls._cache:
            raw = SRDRepository().get_feature(index)
            if raw is None:
                return None
            cls._cache[index] = cls._resolve_feature(raw)
        return cls._cache[index]

    @classmethod
    def get_for_class(cls, class_index: str) -> list[FeatureDefinition]:
        cls._ensure_fresh()
        result = []
        for raw in SRDRepository().get_features(class_index=class_index):
            idx = raw["index"]
            if idx not in cls._cache:
                cls._cache[idx] = cls._resolve_feature(raw)
            result.append(cls._cache[idx])
        return result

    @classmethod
    def get_all_definitions(cls) -> list[FeatureDefinition]:
        cls._ensure_fresh()
        cls._load_all()
        return list(cls._cache.values())

    @classmethod
    def invalidate(cls) -> None:
        cls._cache.clear()
        cls._all_loaded = False
        cls._cached_edition = ""
