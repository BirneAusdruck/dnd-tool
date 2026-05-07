from __future__ import annotations

from src.shared.domain.character_builder import (
    derive_sheet_values,
    proficiency_bonus,
    calc_ac,
    build_character_data,
    modifier,
    STANDARD_ARRAY,
    POINT_BUY_COSTS,
    POINT_BUY_BUDGET,
)


class CharacterBuilderService:
    STANDARD_ARRAY: list[int] = STANDARD_ARRAY
    POINT_BUY_COSTS: dict[int, int] = POINT_BUY_COSTS
    POINT_BUY_BUDGET: int = POINT_BUY_BUDGET

    @staticmethod
    def derive_sheet_values(char_data: dict) -> dict:
        return derive_sheet_values(char_data)

    @staticmethod
    def proficiency_bonus(level: int) -> int:
        return proficiency_bonus(level)

    @staticmethod
    def calc_ac(
        armor_name: str | None,
        dex_score: int,
        has_shield: bool,
        class_index: str,
        str_score: int = 10,
        wis_score: int = 10,
        con_score: int = 10,
    ) -> int:
        return calc_ac(armor_name, dex_score, has_shield, class_index, str_score, wis_score, con_score)

    @staticmethod
    def build_character_data(
        name: str,
        edition: str,
        race_index: str,
        subrace_index: str | None,
        class_index: str,
        background_index: str,
        alignment: str,
        base_ability_scores: dict[str, int],
        chosen_skills: list[str],
        chosen_cantrips: list[str] | None = None,
        chosen_spells: list[str] | None = None,
        half_elf_score_choices: list[str] | None = None,
        dragonborn_ancestry: str | None = None,
        personality: str = "",
        ideals: str = "",
        bonds: str = "",
        flaws: str = "",
        notes: str = "",
    ) -> dict:
        return build_character_data(
            name, edition, race_index, subrace_index, class_index, background_index,
            alignment, base_ability_scores, chosen_skills, chosen_cantrips, chosen_spells,
            half_elf_score_choices, dragonborn_ancestry, personality, ideals, bonds, flaws, notes,
        )

    @staticmethod
    def modifier(score: int) -> int:
        return modifier(score)
