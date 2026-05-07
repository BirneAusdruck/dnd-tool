from __future__ import annotations

from src.shared.domain.dice import roll, DiceResult


class DiceSystem:
    """Stateless wrapper around the dice engine with game-aware helper methods."""

    @staticmethod
    def roll(notation: str) -> DiceResult:
        return roll(notation)

    @staticmethod
    def roll_d20() -> DiceResult:
        return roll("1d20")

    @staticmethod
    def roll_initiative(dex_modifier: int) -> int:
        result = roll("1d20")
        return result.total + dex_modifier

    @staticmethod
    def roll_ability_check(
        ability_score: int,
        proficiency_bonus: int = 0,
        proficient: bool = False,
        expertise: bool = False,
        advantage: bool = False,
        disadvantage: bool = False,
    ) -> DiceResult:
        notation = "adv" if advantage else ("dis" if disadvantage else "1d20")
        result = roll(notation)
        mod = (ability_score - 10) // 2
        if expertise:
            mod += proficiency_bonus * 2
        elif proficient:
            mod += proficiency_bonus
        return DiceResult(
            notation=notation,
            rolls=result.rolls,
            kept=result.kept,
            modifier=mod,
            total=result.total + mod,
            sides=20,
            label=result.label,
            is_critical=result.is_critical,
            is_fumble=result.is_fumble,
        )

    @staticmethod
    def roll_saving_throw(
        ability_score: int,
        proficiency_bonus: int,
        proficient: bool,
        advantage: bool = False,
        disadvantage: bool = False,
    ) -> DiceResult:
        return DiceSystem.roll_ability_check(
            ability_score,
            proficiency_bonus=proficiency_bonus,
            proficient=proficient,
            advantage=advantage,
            disadvantage=disadvantage,
        )

    @staticmethod
    def roll_attack(attack_bonus: int) -> DiceResult:
        result = roll("1d20")
        return DiceResult(
            notation="1d20",
            rolls=result.rolls,
            kept=result.kept,
            modifier=attack_bonus,
            total=result.total + attack_bonus,
            sides=20,
            label="Angriff",
            is_critical=result.is_critical,
            is_fumble=result.is_fumble,
        )

    @staticmethod
    def roll_damage(notation: str, crit: bool = False) -> DiceResult:
        result = roll(notation)
        if crit:
            # Double the dice on a crit (add an equal roll)
            bonus_result = roll(notation)
            total = result.total + bonus_result.total
            return DiceResult(
                notation=f"{notation} (crit)",
                rolls=result.rolls + bonus_result.rolls,
                kept=result.kept + bonus_result.kept,
                modifier=0,
                total=total,
                sides=result.sides,
                label="Kritisch",
            )
        return result

    @staticmethod
    def roll_hp_for_level(hit_die: int, con_modifier: int) -> int:
        result = roll(f"1d{hit_die}")
        return max(1, result.total + con_modifier)

    @staticmethod
    def roll_ability_scores() -> list[int]:
        from src.shared.domain.dice import roll_ability_scores
        return roll_ability_scores()
