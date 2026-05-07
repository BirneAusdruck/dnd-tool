from __future__ import annotations

from src.shared.domain.level_manager import (
    can_level_up, can_level_down,
    apply_level_up, apply_level_down,
    get_level_up_info, get_level_down_info,
    get_asi_levels, get_new_features,
    get_cantrip_scaling_tier, get_combined_caster_level,
    get_multiclass_spell_slots, is_multiclass_spellcaster, get_pact_slots,
)


class LevelUpService:
    @staticmethod
    def can_level_up(char_data: dict) -> bool:
        return can_level_up(char_data)

    @staticmethod
    def can_level_down(char_data: dict) -> bool:
        return can_level_down(char_data)

    @staticmethod
    def apply_level_up(
        char_data: dict,
        hp_gain: int,
        class_index: str | None = None,
        asi_changes: dict | None = None,
        feat_index: str | None = None,
        subclass_index: str | None = None,
    ) -> dict:
        return apply_level_up(char_data, hp_gain, class_index, asi_changes, feat_index, subclass_index)

    @staticmethod
    def apply_level_down(char_data: dict) -> dict:
        return apply_level_down(char_data)

    @staticmethod
    def get_level_up_info(char_data: dict, class_index: str | None = None) -> dict:
        return get_level_up_info(char_data, class_index)

    @staticmethod
    def get_level_down_info(char_data: dict) -> dict:
        return get_level_down_info(char_data)

    @staticmethod
    def get_asi_levels(class_index: str) -> set[int]:
        return get_asi_levels(class_index)

    @staticmethod
    def get_new_features(class_index: str, level: int) -> list[str]:
        return get_new_features(class_index, level)

    @staticmethod
    def get_cantrip_scaling_tier(total_level: int) -> int:
        return get_cantrip_scaling_tier(total_level)

    @staticmethod
    def get_combined_caster_level(classes: list[dict]) -> int:
        return get_combined_caster_level(classes)

    @staticmethod
    def get_multiclass_spell_slots(combined_caster_level: int) -> list[int]:
        return get_multiclass_spell_slots(combined_caster_level)

    @staticmethod
    def is_multiclass_spellcaster(classes: list[dict]) -> bool:
        return is_multiclass_spellcaster(classes)

    @staticmethod
    def get_pact_slots(warlock_level: int) -> tuple[int, int]:
        return get_pact_slots(warlock_level)
