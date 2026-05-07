from __future__ import annotations

from src.shared.runtime.character import Character
from src.shared.runtime.active_effect import ActiveEffect
from src.shared.runtime.combat_encounter import CombatantEntry

# Conditions that impose disadvantage on attack rolls
_ATTACK_DISADVANTAGE = {"Blinded", "Poisoned", "Frightened", "Prone", "Restrained"}
# Conditions that grant attackers advantage against the target
_GRANT_ADVANTAGE_TO_ATTACKERS = {"Blinded", "Paralyzed", "Petrified", "Prone", "Stunned", "Unconscious"}
# Conditions that prevent actions
_INCAPACITATED = {"Incapacitated", "Paralyzed", "Petrified", "Stunned", "Unconscious"}


class EffectResolutionSystem:
    """Resolves conditions and active effects on characters and combatants.

    Works exclusively with runtime objects — no repository or JSON access.
    """

    # ── Character conditions ───────────────────────────────────────────────

    @staticmethod
    def apply_condition(character: Character, condition: str) -> None:
        character.add_condition(condition)

    @staticmethod
    def remove_condition(character: Character, condition: str) -> None:
        character.remove_condition(condition)

    @staticmethod
    def is_incapacitated(character: Character) -> bool:
        return any(c in _INCAPACITATED for c in character.conditions)

    @staticmethod
    def has_attack_disadvantage(character: Character) -> bool:
        return any(c in _ATTACK_DISADVANTAGE for c in character.conditions)

    @staticmethod
    def grants_advantage_to_attackers(character: Character) -> bool:
        return any(c in _GRANT_ADVANTAGE_TO_ATTACKERS for c in character.conditions)

    # ── ActiveEffect lifecycle ─────────────────────────────────────────────

    @staticmethod
    def tick_effects(combatant: CombatantEntry) -> list[ActiveEffect]:
        """Advance all effects by one round. Returns the list of newly expired effects."""
        expired: list[ActiveEffect] = []
        for effect in list(combatant.effects):
            effect.tick()
            if effect.is_expired:
                expired.append(effect)
        return expired

    @staticmethod
    def remove_expired(combatant: CombatantEntry) -> list[ActiveEffect]:
        """Remove expired effects from combatant. Returns removed effects."""
        expired = [e for e in combatant.effects if e.is_expired]
        combatant.effects = [e for e in combatant.effects if not e.is_expired]
        return expired

    @staticmethod
    def add_effect(combatant: CombatantEntry, effect: ActiveEffect) -> None:
        combatant.effects.append(effect)

    @staticmethod
    def remove_effect_by_name(combatant: CombatantEntry, name: str) -> None:
        combatant.effects = [e for e in combatant.effects if e.name != name]

    @staticmethod
    def has_effect(combatant: CombatantEntry, name: str) -> bool:
        return any(e.name == name for e in combatant.effects)

    # ── Concentration ──────────────────────────────────────────────────────

    @staticmethod
    def concentration_check(character: Character, damage_taken: int) -> bool:
        """
        DC = max(10, damage/2). Returns True if the check succeeds.
        Uses DiceSystem indirectly to avoid circular imports.
        """
        from src.shared.systems.dice_system import DiceSystem
        dc = max(10, damage_taken // 2)
        con_score = character.ability_scores.get("CON", 10)
        proficient = character.is_proficient_in_save("CON")
        result = DiceSystem.roll_saving_throw(
            con_score, character.proficiency_bonus, proficient
        )
        return result.total >= dc
