from __future__ import annotations

from src.shared.domain.definitions.effect_definition import EffectDefinition
from src.shared.repositories.srd_repository import SRDRepository, get_active_edition
from src.shared.domain.srd_constants import EffectCondition, EffectType


class EffectService:
    _cache: dict[str, EffectDefinition] = {}
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
    def _from_raw(cls, raw: dict) -> EffectDefinition:
        return EffectDefinition(
            index=raw["index"],
            effect_type=EffectType(raw["effect_type"]),
            target=raw["target"],
            value=raw.get("value"),
            condition=EffectCondition(raw["condition"]) if raw.get("condition") else None,
        )

    @classmethod
    def _load_all(cls) -> None:
        if cls._all_loaded:
            return
        for raw in SRDRepository().get_effects():
            idx = raw["index"]
            if idx not in cls._cache:
                cls._cache[idx] = cls._from_raw(raw)
        cls._all_loaded = True

    @classmethod
    def get_definition(cls, index: str) -> EffectDefinition | None:
        cls._ensure_fresh()
        if index not in cls._cache:
            raw = SRDRepository().get_effect(index)
            if raw is None:
                return None
            cls._cache[index] = cls._from_raw(raw)
        return cls._cache[index]

    @classmethod
    def get_all_definitions(cls) -> list[EffectDefinition]:
        cls._ensure_fresh()
        cls._load_all()
        return list(cls._cache.values())

    @classmethod
    def invalidate(cls) -> None:
        cls._cache.clear()
        cls._all_loaded = False
        cls._cached_edition = ""
