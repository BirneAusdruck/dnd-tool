"""
Dice expression parser and roller.

Supported formats:
  d20 / 1d20          one d20
  2d6+3               two d6 plus modifier
  4d6kh3              keep highest 3 (ability score generation)
  2d20kl1             keep lowest 1 (disadvantage)
  adv / vorteil       shortcut: 2d20kh1
  dis / nachteil      shortcut: 2d20kl1
"""
from __future__ import annotations
import re
import random
from dataclasses import dataclass, field

_EXPR_RE = re.compile(
    r"^(?P<count>\d+)?d(?P<sides>\d+)"
    r"(?:kh(?P<kh>\d+)|kl(?P<kl>\d+))?"
    r"(?P<mod>[+-]\d+)?$",
    re.IGNORECASE,
)

_VALID_SIDES = {4, 6, 8, 10, 12, 20, 100}


@dataclass
class DiceResult:
    notation:    str
    rolls:       list[int]
    kept:        list[int]
    modifier:    int
    total:       int
    sides:       int
    label:       str = ""
    is_critical: bool = False
    is_fumble:   bool = False

    def to_dict(self) -> dict:
        return {
            "notation":    self.notation,
            "rolls":       self.rolls,
            "kept":        self.kept,
            "modifier":    self.modifier,
            "total":       self.total,
            "sides":       self.sides,
            "label":       self.label,
            "is_critical": self.is_critical,
            "is_fumble":   self.is_fumble,
        }

    def format(self) -> str:
        rolls_str = ", ".join(str(r) for r in self.rolls)
        parts = [f"[{rolls_str}]"]
        if self.rolls != self.kept:
            parts.append(f"→ [{', '.join(str(r) for r in self.kept)}]")
        if self.modifier > 0:
            parts.append(f"+{self.modifier}")
        elif self.modifier < 0:
            parts.append(str(self.modifier))
        parts.append(f"= {self.total}")
        if self.label:
            parts.append(f"({self.label})")
        return " ".join(parts)


def roll(notation: str) -> DiceResult:
    """Parse and roll a dice expression. Raises ValueError on bad input."""
    clean = notation.strip().lower().replace(" ", "")

    if clean in ("adv", "vorteil", "advantage"):
        r1, r2 = random.randint(1, 20), random.randint(1, 20)
        best = max(r1, r2)
        return DiceResult(
            notation=notation, rolls=[r1, r2], kept=[best],
            modifier=0, total=best, sides=20, label="Vorteil",
            is_critical=(best == 20), is_fumble=False,
        )
    if clean in ("dis", "nachteil", "disadvantage"):
        r1, r2 = random.randint(1, 20), random.randint(1, 20)
        worst = min(r1, r2)
        return DiceResult(
            notation=notation, rolls=[r1, r2], kept=[worst],
            modifier=0, total=worst, sides=20, label="Nachteil",
            is_critical=False, is_fumble=(worst == 1),
        )

    m = _EXPR_RE.match(clean)
    if not m:
        raise ValueError(f"Ungültiger Würfelausdruck: {notation!r}")

    count = int(m.group("count") or 1)
    sides = int(m.group("sides"))
    kh    = int(m.group("kh"))  if m.group("kh")  else None
    kl    = int(m.group("kl"))  if m.group("kl")  else None
    mod   = int(m.group("mod") or 0)

    count = max(1, min(count, 100))
    sides = max(2, min(sides, 1000))

    rolls = [random.randint(1, sides) for _ in range(count)]

    if kh is not None:
        kept = sorted(rolls, reverse=True)[: max(1, kh)]
    elif kl is not None:
        kept = sorted(rolls)[: max(1, kl)]
    else:
        kept = rolls[:]

    total = sum(kept) + mod
    is_crit   = (len(kept) == 1 and sides == 20 and kept[0] == 20)
    is_fumble = (len(kept) == 1 and sides == 20 and kept[0] == 1)

    return DiceResult(
        notation=notation, rolls=rolls, kept=kept,
        modifier=mod, total=total, sides=sides, label="",
        is_critical=is_crit, is_fumble=is_fumble,
    )


def roll_ability_scores() -> list[int]:
    """Roll 4d6kh3 six times (standard ability score method)."""
    scores = []
    for _ in range(6):
        four = sorted(random.randint(1, 6) for _ in range(4))
        scores.append(sum(four[1:]))
    return scores
