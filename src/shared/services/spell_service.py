from __future__ import annotations

from src.shared.domain.definitions.spell_definition import SpellDefinition
from src.shared.factories.spell_factory import SpellFactory
from src.shared.repositories.srd_repository import SRDRepository, get_active_edition


class SpellService:
    # keyed by lowercase spell name
    _cache: dict[str, SpellDefinition] = {}
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
        for raw in SRDRepository().get_spells():
            key = raw["name"].lower()
            if key not in cls._cache:
                cls._cache[key] = SpellFactory.create(raw)
        cls._all_loaded = True

    @classmethod
    def get(cls, name: str) -> SpellDefinition | None:
        cls._ensure_fresh()
        key = name.lower()
        if key not in cls._cache:
            raw = SRDRepository().get_spell(name)
            if raw is None:
                return None
            cls._cache[key] = SpellFactory.create(raw)
        return cls._cache[key]

    @classmethod
    def get_all(cls) -> list[SpellDefinition]:
        cls._ensure_fresh()
        cls._load_all()
        return sorted(cls._cache.values(), key=lambda s: (s.level, s.name))

    @classmethod
    def get_for_class(
        cls,
        class_index: str,
        level: int | None = None,
    ) -> list[SpellDefinition]:
        cls._ensure_fresh()
        cls._load_all()
        spells = [s for s in cls._cache.values() if s.available_to(class_index)]
        if level is not None:
            spells = [s for s in spells if s.level == level]
        return sorted(spells, key=lambda s: (s.level, s.name))

    @classmethod
    def get_cantrips(cls, class_index: str) -> list[SpellDefinition]:
        return cls.get_for_class(class_index, level=0)

    @classmethod
    def get_cantrips_raw(cls, class_index: str) -> list[dict]:
        return SRDRepository().get_cantrips(class_index)

    @classmethod
    def get_spells_raw(
        cls, class_index: str | None = None, level: int | None = None
    ) -> list[dict]:
        return SRDRepository().get_spells(class_index=class_index, level=level)

    @classmethod
    def invalidate(cls) -> None:
        cls._cache.clear()
        cls._all_loaded = False
        cls._cached_edition = ""
