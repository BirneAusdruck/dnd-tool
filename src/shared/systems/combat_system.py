from __future__ import annotations

from src.shared.runtime.character import Character
from src.shared.runtime.combat_encounter import CombatEncounter, CombatantEntry
from src.shared.systems.dice_system import DiceSystem

_ARMOR_AC: dict[str, dict] = {
    "Padded":           {"base": 11, "dex": "full"},
    "Leather":          {"base": 11, "dex": "full"},
    "Studded Leather":  {"base": 12, "dex": "full"},
    "Hide":             {"base": 12, "dex": 2},
    "Chain Shirt":      {"base": 13, "dex": 2},
    "Scale Mail":       {"base": 14, "dex": 2},
    "Breastplate":      {"base": 14, "dex": 2},
    "Half Plate":       {"base": 15, "dex": 2},
    "Ring Mail":        {"base": 14, "dex": 0},
    "Chain Mail":       {"base": 16, "dex": 0},
    "Splint":           {"base": 17, "dex": 0},
    "Plate":            {"base": 18, "dex": 0},
}


class CombatSystem:
    """Stateless combat rules engine.

    Works with Character and CombatEncounter runtime objects only.
    No repository or JSON access.
    """

    # ── Encounter setup ────────────────────────────────────────────────────

    @staticmethod
    def build_combatant(
        character: Character,
        character_id: int | None = None,
    ) -> CombatantEntry:
        return CombatantEntry(
            name=character.name,
            initiative=0,
            hp_current=character.hp_current,
            hp_max=character.hp_max,
            is_player=True,
            character_id=character_id,
        )

    @staticmethod
    def roll_initiative_for(combatant: CombatantEntry, dex_modifier: int) -> None:
        combatant.initiative = DiceSystem.roll_initiative(dex_modifier)

    # ── AC calculation ─────────────────────────────────────────────────────

    @staticmethod
    def calculate_ac(character: Character) -> int:
        dex_mod = character.ability_modifier("DEX")
        shield_bonus = 2 if character.has_shield else 0
        armor_name = character.equipped_armor

        if armor_name and armor_name in _ARMOR_AC:
            entry = _ARMOR_AC[armor_name]
            dex_cap = entry["dex"]
            if dex_cap == "full":
                return entry["base"] + dex_mod + shield_bonus
            return entry["base"] + min(dex_mod, dex_cap) + shield_bonus

        # Unarmored defense
        if character.primary_class_index == "barbarian":
            con_mod = character.ability_modifier("CON")
            return 10 + dex_mod + con_mod + shield_bonus
        if character.primary_class_index == "monk":
            wis_mod = character.ability_modifier("WIS")
            return 10 + dex_mod + wis_mod

        return 10 + dex_mod + shield_bonus

    # ── Attack resolution ──────────────────────────────────────────────────

    @staticmethod
    def is_hit(attack_total: int, target_ac: int) -> bool:
        return attack_total >= target_ac

    @staticmethod
    def resolve_attack(
        attacker_bonus: int,
        target_ac: int,
        damage_notation: str,
        advantage: bool = False,
        disadvantage: bool = False,
    ) -> dict:
        notation = "adv" if advantage else ("dis" if disadvantage else "1d20")
        attack_roll = DiceSystem.roll(notation)
        total = attack_roll.total + attacker_bonus

        hit = attack_roll.is_critical or (
            not attack_roll.is_fumble and total >= target_ac
        )
        damage = DiceSystem.roll_damage(damage_notation, crit=attack_roll.is_critical) if hit else None

        return {
            "attack_roll": attack_roll,
            "attack_total": total,
            "hit": hit,
            "critical": attack_roll.is_critical,
            "fumble": attack_roll.is_fumble,
            "damage": damage,
        }

    # ── Damage & healing ───────────────────────────────────────────────────

    @staticmethod
    def apply_damage(combatant: CombatantEntry, amount: int) -> None:
        combatant.hp_current = max(0, combatant.hp_current - amount)

    @staticmethod
    def apply_healing(combatant: CombatantEntry, amount: int) -> None:
        combatant.hp_current = min(combatant.hp_max, combatant.hp_current + amount)

    # ── Saving throw ───────────────────────────────────────────────────────

    @staticmethod
    def roll_saving_throw(
        character: Character,
        ability: str,
        dc: int,
        advantage: bool = False,
        disadvantage: bool = False,
    ) -> dict:
        score = character.ability_scores.get(ability, 10)
        proficient = character.is_proficient_in_save(ability)
        result = DiceSystem.roll_saving_throw(
            score, character.proficiency_bonus, proficient,
            advantage=advantage, disadvantage=disadvantage,
        )
        return {
            "roll": result,
            "total": result.total,
            "success": result.total >= dc,
            "dc": dc,
        }
