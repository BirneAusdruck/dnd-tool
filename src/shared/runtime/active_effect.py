from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ActiveEffect:
    """A temporary condition or magical effect on a character or combatant."""

    name: str
    source: str              # spell name, item, ability, etc.
    description: str = ""
    duration_rounds: int | None = None   # None = lasts until dispelled
    rounds_remaining: int | None = None

    def __post_init__(self) -> None:
        if self.duration_rounds is not None and self.rounds_remaining is None:
            self.rounds_remaining = self.duration_rounds

    @property
    def is_permanent(self) -> bool:
        return self.duration_rounds is None

    @property
    def is_expired(self) -> bool:
        return self.rounds_remaining is not None and self.rounds_remaining <= 0

    def tick(self) -> None:
        """Advance one round. Call at the start of each affected creature's turn."""
        if self.rounds_remaining is not None:
            self.rounds_remaining = max(0, self.rounds_remaining - 1)
