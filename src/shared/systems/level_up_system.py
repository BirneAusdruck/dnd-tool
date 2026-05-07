from __future__ import annotations

from src.shared.runtime.character import Character, CharacterClass
from src.shared.services.class_service import ClassService

# PHB combined spell slot table (index 0 = combined caster level 1)
_MULTICLASS_SLOTS: list[list[int]] = [
    [2, 0, 0, 0, 0, 0, 0, 0, 0],
    [3, 0, 0, 0, 0, 0, 0, 0, 0],
    [4, 2, 0, 0, 0, 0, 0, 0, 0],
    [4, 3, 0, 0, 0, 0, 0, 0, 0],
    [4, 3, 2, 0, 0, 0, 0, 0, 0],
    [4, 3, 3, 0, 0, 0, 0, 0, 0],
    [4, 3, 3, 1, 0, 0, 0, 0, 0],
    [4, 3, 3, 2, 0, 0, 0, 0, 0],
    [4, 3, 3, 3, 1, 0, 0, 0, 0],
    [4, 3, 3, 3, 2, 0, 0, 0, 0],
    [4, 3, 3, 3, 2, 1, 0, 0, 0],
    [4, 3, 3, 3, 2, 1, 0, 0, 0],
    [4, 3, 3, 3, 2, 1, 1, 0, 0],
    [4, 3, 3, 3, 2, 1, 1, 0, 0],
    [4, 3, 3, 3, 2, 1, 1, 1, 0],
    [4, 3, 3, 3, 2, 1, 1, 1, 0],
    [4, 3, 3, 3, 2, 1, 1, 1, 1],
    [4, 3, 3, 3, 3, 1, 1, 1, 1],
    [4, 3, 3, 3, 3, 2, 1, 1, 1],
    [4, 3, 3, 3, 3, 2, 2, 1, 1],
]

_PACT_SLOT_LEVEL: list[int] = [
    1, 1, 2, 2, 3, 3, 4, 4, 5, 5,
    5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
]


class LevelUpSystem:
    """Rules for leveling up and down a Character object.

    Works exclusively with Character runtime objects and ClassDefinition
    domain objects — no repository or JSON access.
    """

    # ── Queries ────────────────────────────────────────────────────────────

    @staticmethod
    def can_level_up(character: Character) -> bool:
        return character.level < 20

    @staticmethod
    def can_level_down(character: Character) -> bool:
        return character.level > 1

    # ── Caster helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _caster_weight(class_index: str, subclass: str | None = None) -> float | str:
        cls_def = ClassService.get(class_index)
        if not cls_def or not cls_def.spellcasting:
            if class_index == "fighter" and subclass and "Eldritch Knight" in subclass:
                return 1 / 3
            if class_index == "rogue" and subclass and "Arcane Trickster" in subclass:
                return 1 / 3
            return 0.0
        if cls_def.spellcasting.type == "pact":
            return "pact"
        if cls_def.spellcasting.slots and cls_def.spellcasting.slots[0][0] == 0:
            return 0.5
        return 1.0

    @staticmethod
    def _combined_caster_level(classes: list[CharacterClass]) -> int:
        total = 0.0
        for c in classes:
            w = LevelUpSystem._caster_weight(c.class_index, c.subclass)
            if isinstance(w, float) and w > 0:
                total += c.level * w
        return int(total)

    @staticmethod
    def _multiclass_spell_slots(combined: int) -> list[int]:
        if combined <= 0:
            return []
        return list(_MULTICLASS_SLOTS[min(combined - 1, len(_MULTICLASS_SLOTS) - 1)])

    @staticmethod
    def _pact_slots(warlock_level: int) -> tuple[int, int]:
        if warlock_level <= 0:
            return (0, 0)
        cls_def = ClassService.get("warlock")
        idx = min(warlock_level - 1, len(_PACT_SLOT_LEVEL) - 1)
        count = (
            cls_def.spellcasting.slots[idx][0]
            if cls_def and cls_def.spellcasting
            else 0
        )
        return (count, _PACT_SLOT_LEVEL[idx])

    @staticmethod
    def _is_multiclass_caster(classes: list[CharacterClass]) -> bool:
        return sum(
            1 for c in classes
            if LevelUpSystem._caster_weight(c.class_index, c.subclass) not in (0.0, "pact")
        ) > 1

    # ── Level-up info (for the dialog) ────────────────────────────────────

    @staticmethod
    def get_level_up_info(
        character: Character,
        class_index: str | None = None,
    ) -> dict:
        cls_idx = class_index or character.primary_class_index
        cls_def = ClassService.get(cls_idx)

        total_level = character.level
        new_total = total_level + 1

        cls_entry = next(
            (c for c in character.classes if c.class_index == cls_idx), None
        )
        class_level = cls_entry.level if cls_entry else 0
        new_class_level = class_level + 1

        hit_die = cls_def.hit_die if cls_def else 8
        con_mod = (character.ability_scores.get("CON", 10) - 10) // 2

        new_features = list(cls_def.features_at(new_class_level)) if cls_def else []
        is_asi = new_class_level in (cls_def.asi_levels() if cls_def else {4, 8, 12, 16, 19})

        is_subclass = (
            cls_def is not None
            and new_class_level == cls_def.subclass_level
            and (cls_entry is None or not cls_entry.subclass)
        )
        subclass_choices = list(cls_def.subclasses) if is_subclass and cls_def else []

        # Simulate "after" class list for slot calculation
        after_classes = [
            CharacterClass(c.class_index, c.level + 1, c.subclass)
            if c.class_index == cls_idx else c
            for c in character.classes
        ]
        if cls_idx not in {c.class_index for c in character.classes}:
            after_classes = list(character.classes) + [
                CharacterClass(cls_idx, 1, None)
            ]

        multiclass = LevelUpSystem._is_multiclass_caster(after_classes)
        wl_entry = next((c for c in character.classes if c.class_index == "warlock"), None)
        old_pact = LevelUpSystem._pact_slots(wl_entry.level if wl_entry else 0)
        wl_after = next((c for c in after_classes if c.class_index == "warlock"), None)
        new_pact = LevelUpSystem._pact_slots(wl_after.level if wl_after else 0)

        spell_info = None
        if cls_def and cls_def.spellcasting:
            sc = cls_def.spellcasting
            if multiclass:
                old_slots = LevelUpSystem._multiclass_spell_slots(
                    LevelUpSystem._combined_caster_level(character.classes)
                )
                new_slots = LevelUpSystem._multiclass_spell_slots(
                    LevelUpSystem._combined_caster_level(after_classes)
                )
            else:
                old_slots = list(cls_def.spell_slots_at(class_level)) if class_level > 0 else []
                new_slots = list(cls_def.spell_slots_at(new_class_level))

            cntrp = sc.cantrips_known
            old_cantrips = cntrp[class_level - 1] if 0 < class_level <= len(cntrp) else 0
            new_cantrips = cntrp[new_class_level - 1] if new_class_level <= len(cntrp) else 0

            new_spell_count = 0
            if sc.type == "known" and sc.spells_known:
                old_known = sc.spells_known[class_level - 1] if 0 < class_level <= len(sc.spells_known) else 0
                new_known = sc.spells_known[new_class_level - 1] if new_class_level <= len(sc.spells_known) else 0
                new_spell_count = max(0, new_known - old_known)

            spell_info = {
                "ability": sc.ability,
                "type": sc.type,
                "is_multiclass": multiclass,
                "old_slots": old_slots,
                "new_slots": new_slots,
                "old_pact": old_pact,
                "new_pact": new_pact,
                "gained_cantrip": new_cantrips > old_cantrips,
                "new_spell_count": new_spell_count,
            }
        elif old_pact != new_pact:
            spell_info = {
                "ability": "CHA", "type": "pact", "is_multiclass": multiclass,
                "old_slots": [], "new_slots": [],
                "old_pact": old_pact, "new_pact": new_pact,
                "gained_cantrip": False, "new_spell_count": 0,
            }

        return {
            "class_index": cls_idx,
            "total_level": total_level,
            "new_total_level": new_total,
            "class_level": class_level,
            "new_class_level": new_class_level,
            "current_level": total_level,
            "new_level": new_total,
            "hit_die": hit_die,
            "con_mod": con_mod,
            "hp_average": max(1, hit_die // 2 + 1 + con_mod),
            "new_features": new_features,
            "is_asi": is_asi,
            "is_subclass": is_subclass,
            "subclass_name": cls_def.subclass_name if cls_def else "",
            "subclass_choices": subclass_choices,
            "spell_info": spell_info,
            "current_scores": dict(character.ability_scores),
        }

    # ── Apply level-up (mutates Character) ────────────────────────────────

    @staticmethod
    def apply(
        character: Character,
        hp_gain: int,
        class_index: str,
        asi_changes: dict[str, int] | None = None,
        feat_index: str | None = None,
        subclass_index: str | None = None,
    ) -> None:
        entry = next(
            (c for c in character.classes if c.class_index == class_index), None
        )
        if entry:
            entry.level += 1
        else:
            character.classes.append(CharacterClass(class_index, 1, None))

        new_total = character.level   # level property recomputes from classes

        character.level_history.append(
            {"total_level": new_total, "class_index": class_index}
        )

        cls_def = ClassService.get(class_index)
        hit_die = cls_def.hit_die if cls_def else 8
        character.hit_dice_str = f"{new_total}d{hit_die}"

        character.hp_max += hp_gain
        character.hp_current += hp_gain
        character.hp_level_history.append(hp_gain)

        if subclass_index:
            target = next(
                (c for c in character.classes if c.class_index == class_index), None
            )
            if target:
                target.subclass = subclass_index

        if feat_index:
            if feat_index not in character.feats:
                character.feats.append(feat_index)
            character.feat_history.append({
                "total_level": new_total,
                "class_index": class_index,
                "feat_index": feat_index,
            })
        elif asi_changes:
            for ability, delta in asi_changes.items():
                if ability in character.ability_scores:
                    character.ability_scores[ability] = min(
                        20, character.ability_scores[ability] + delta
                    )
            character.asi_history.append({
                "total_level": new_total,
                "class_index": class_index,
                "changes": dict(asi_changes),
            })

    # ── Revert last level-up (mutates Character) ───────────────────────────

    @staticmethod
    def revert(character: Character) -> None:
        if character.level <= 1:
            return

        removed_level = character.level

        lvl_hist = character.level_history
        if lvl_hist and lvl_hist[-1]["total_level"] == removed_level:
            cls_idx = lvl_hist.pop()["class_index"]
        else:
            cls_idx = character.primary_class_index

        # Undo feat
        feat_hist = character.feat_history
        if feat_hist and feat_hist[-1]["total_level"] == removed_level:
            feat_idx = feat_hist.pop()["feat_index"]
            if feat_idx in character.feats:
                character.feats.remove(feat_idx)

        # Undo ASI
        asi_hist = character.asi_history
        if asi_hist and asi_hist[-1]["total_level"] == removed_level:
            for ability, delta in asi_hist.pop()["changes"].items():
                if ability in character.ability_scores:
                    character.ability_scores[ability] = max(
                        1, character.ability_scores[ability] - delta
                    )

        # Undo HP
        if len(character.hp_level_history) >= removed_level:
            hp_removed = character.hp_level_history.pop()
            character.hp_max = max(1, character.hp_max - hp_removed)
            character.hp_current = min(character.hp_current, character.hp_max)

        # Decrement class
        cls_entry = next(
            (c for c in character.classes if c.class_index == cls_idx), None
        )
        if cls_entry:
            cls_def = ClassService.get(cls_idx)
            if cls_def and cls_entry.level == cls_def.subclass_level:
                cls_entry.subclass = None
            cls_entry.level -= 1
            if cls_entry.level <= 0:
                character.classes = [
                    c for c in character.classes if c.class_index != cls_idx
                ]

        # Update hit dice string
        primary_def = ClassService.get(character.primary_class_index)
        hd = primary_def.hit_die if primary_def else 8
        character.hit_dice_str = f"{character.level}d{hd}"
