from __future__ import annotations

from src.shared.domain.definitions.class_definition import ClassDefinition
from src.shared.factories.class_factory import ClassFactory
from src.shared.repositories.srd_repository import SRDRepository, get_active_edition


class ClassService:
    _cache: dict[str, ClassDefinition] = {}
    _cached_edition: str = ""

    @classmethod
    def _ensure_fresh(cls) -> None:
        current = get_active_edition()
        if cls._cached_edition != current:
            cls._cache.clear()
            cls._cached_edition = current

    @classmethod
    def _resolve(cls, raw: dict) -> ClassDefinition:
        """Enrich raw class dict with resolved features and effects."""
        repo = SRDRepository()
        features_resolved: dict[str, list[dict]] = {}
        for level_str, feat_indices in raw.get("features", {}).items():
            resolved = []
            for feat_idx in feat_indices:
                feat_raw = repo.get_feature(feat_idx)
                if feat_raw is None:
                    continue
                # resolve effect indices → inline effect dicts
                effects_resolved = []
                for eff_item in feat_raw.get("effects", []):
                    if isinstance(eff_item, str):
                        eff = repo.get_effect(eff_item)
                        if eff:
                            effects_resolved.append(eff)
                    elif isinstance(eff_item, dict):
                        effects_resolved.append(eff_item)
                resolved.append({**feat_raw, "effects": effects_resolved})
            features_resolved[level_str] = resolved
        return ClassFactory.create({**raw, "features_resolved": features_resolved})

    @classmethod
    def get(cls, index: str) -> ClassDefinition | None:
        cls._ensure_fresh()
        if index not in cls._cache:
            raw = SRDRepository().get_class(index)
            if raw is None:
                return None
            cls._cache[index] = cls._resolve(raw)
        return cls._cache[index]

    # Alias kept for backwards compatibility
    @classmethod
    def get_definition(cls, index: str) -> ClassDefinition | None:
        return cls.get(index)

    @classmethod
    def get_all(cls) -> list[ClassDefinition]:
        cls._ensure_fresh()
        for raw in SRDRepository().get_classes():
            idx = raw["index"]
            if idx not in cls._cache:
                cls._cache[idx] = cls._resolve(raw)
        return list(cls._cache.values())

    @classmethod
    def get_raw(cls, index: str) -> dict | None:
        return SRDRepository().get_class(index)

    @classmethod
    def get_all_raw(cls) -> list[dict]:
        return SRDRepository().get_classes()

    @classmethod
    def invalidate(cls) -> None:
        cls._cache.clear()
        cls._cached_edition = ""
