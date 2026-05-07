from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CombatantEntry:
    name: str
    initiative: int
    hp_current: int
    hp_max: int
    is_player: bool
    character_id: int | None = None   # set for PC entries
    effects: list = field(default_factory=list)   # list[ActiveEffect]

    @property
    def is_alive(self) -> bool:
        return self.hp_current > 0

    @property
    def is_unconscious(self) -> bool:
        return self.hp_current == 0


@dataclass
class CombatEncounter:
    """Tracks the full state of an active combat encounter."""

    combatants: list[CombatantEntry] = field(default_factory=list)
    round_number: int = 1
    current_turn_index: int = 0
    is_active: bool = False

    # ── Setup ──────────────────────────────────────────────────────────────

    def add_combatant(self, entry: CombatantEntry) -> None:
        self.combatants.append(entry)

    def remove_combatant(self, name: str) -> None:
        self.combatants = [c for c in self.combatants if c.name != name]

    def sort_by_initiative(self) -> None:
        self.combatants.sort(key=lambda c: c.initiative, reverse=True)
        self.current_turn_index = 0

    def start(self) -> None:
        self.sort_by_initiative()
        self.round_number = 1
        self.current_turn_index = 0
        self.is_active = True

    def end(self) -> None:
        self.is_active = False

    # ── Turn management ────────────────────────────────────────────────────

    @property
    def current_combatant(self) -> CombatantEntry | None:
        if not self.combatants:
            return None
        return self.combatants[self.current_turn_index % len(self.combatants)]

    def next_turn(self) -> CombatantEntry | None:
        if not self.combatants:
            return None
        self.current_turn_index += 1
        if self.current_turn_index >= len(self.combatants):
            self.current_turn_index = 0
            self.round_number += 1
        return self.current_combatant

    # ── Queries ────────────────────────────────────────────────────────────

    @property
    def alive_combatants(self) -> list[CombatantEntry]:
        return [c for c in self.combatants if c.is_alive]

    @property
    def players_alive(self) -> bool:
        return any(c.is_player and c.is_alive for c in self.combatants)

    @property
    def enemies_alive(self) -> bool:
        return any(not c.is_player and c.is_alive for c in self.combatants)

    @property
    def is_over(self) -> bool:
        return not self.players_alive or not self.enemies_alive
