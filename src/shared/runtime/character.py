from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CharacterClass:
    class_index: str
    level: int
    subclass: str | None = None


@dataclass
class Character:
    """Mutable runtime state of a single D&D character."""

    # ── Meta ──────────────────────────────────────────────────────────────
    edition: str

    # ── Identity ──────────────────────────────────────────────────────────
    name: str
    race_index: str
    subrace_index: str | None
    background_index: str
    alignment: str
    experience: int
    dragonborn_ancestry: str | None

    # ── Class & progression ───────────────────────────────────────────────
    classes: list[CharacterClass]
    level_history: list[dict]    # [{total_level, class_index}]
    asi_history: list[dict]      # [{total_level, class_index, changes}]
    feats: list[str]
    feat_history: list[dict]     # [{total_level, class_index, feat_index}]

    # ── Ability scores ────────────────────────────────────────────────────
    ability_scores: dict[str, int]

    # ── HP ────────────────────────────────────────────────────────────────
    hp_max: int
    hp_current: int
    hp_temp: int
    hp_level_history: list[int]

    # ── Hit dice ──────────────────────────────────────────────────────────
    hit_dice_str: str   # e.g. "5d8"
    hit_dice_used: int

    # ── Death saves ───────────────────────────────────────────────────────
    death_save_successes: int
    death_save_failures: int

    # ── Proficiencies ─────────────────────────────────────────────────────
    skill_proficiencies: list[str]
    saving_throw_proficiencies: list[str]
    armor_proficiencies: list[str]
    weapon_proficiencies: list[str]
    tool_proficiencies: list[str]
    languages: list[str]

    # ── Equipment ─────────────────────────────────────────────────────────
    equipped_armor: str | None
    has_shield: bool
    equipped_weapons: list[str]
    inventory: list[dict]
    currency: dict[str, int]

    # ── Spellcasting ──────────────────────────────────────────────────────
    cantrips: list[str]
    spells_known: list[str]
    spell_slots_used: list[int]

    # ── Traits & notes ────────────────────────────────────────────────────
    personality: str
    ideals: str
    bonds: str
    flaws: str
    notes: str

    # ── Active conditions ─────────────────────────────────────────────────
    conditions: list[str] = field(default_factory=list)

    # ── Computed properties ───────────────────────────────────────────────

    @property
    def level(self) -> int:
        return sum(c.level for c in self.classes)

    @property
    def primary_class_index(self) -> str:
        return self.classes[0].class_index if self.classes else ""

    @property
    def proficiency_bonus(self) -> int:
        return (self.level - 1) // 4 + 2

    def ability_modifier(self, ability: str) -> int:
        return (self.ability_scores.get(ability, 10) - 10) // 2

    def is_proficient_in_skill(self, skill: str) -> bool:
        return skill in self.skill_proficiencies

    def is_proficient_in_save(self, ability: str) -> bool:
        return ability in self.saving_throw_proficiencies

    def has_condition(self, condition: str) -> bool:
        return condition in self.conditions

    # ── Mutations ─────────────────────────────────────────────────────────

    def take_damage(self, amount: int) -> None:
        if self.hp_temp > 0:
            absorbed = min(self.hp_temp, amount)
            self.hp_temp -= absorbed
            amount -= absorbed
        self.hp_current = max(0, self.hp_current - amount)

    def heal(self, amount: int) -> None:
        self.hp_current = min(self.hp_max, self.hp_current + amount)

    def add_temp_hp(self, amount: int) -> None:
        self.hp_temp = max(self.hp_temp, amount)

    def add_condition(self, condition: str) -> None:
        if condition not in self.conditions:
            self.conditions.append(condition)

    def remove_condition(self, condition: str) -> None:
        self.conditions = [c for c in self.conditions if c != condition]

    def is_alive(self) -> bool:
        return self.hp_current > 0

    def is_unconscious(self) -> bool:
        return self.hp_current == 0

    # ── Serialization ─────────────────────────────────────────────────────

    @classmethod
    def from_dict(cls, data: dict) -> Character:
        basics = data.get("basics", {})
        hp = data.get("hp", {})
        hit_dice = data.get("hit_dice", {})
        death = data.get("death_saves", {})
        profs = data.get("proficiencies", {})
        equip = data.get("equipment", {})
        spells = data.get("spellcasting") or {}
        traits = data.get("traits", {})

        raw_classes = basics.get("classes") or [
            {"class_index": basics.get("class", ""), "level": basics.get("level", 1)}
        ]

        return cls(
            edition=data.get("meta", {}).get("edition", "5.1_srd"),
            name=basics.get("name", ""),
            race_index=basics.get("race", ""),
            subrace_index=basics.get("subrace"),
            background_index=basics.get("background", ""),
            alignment=basics.get("alignment", ""),
            experience=basics.get("experience", 0),
            dragonborn_ancestry=basics.get("dragonborn_ancestry"),
            classes=[
                CharacterClass(
                    class_index=c["class_index"],
                    level=c["level"],
                    subclass=c.get("subclass"),
                )
                for c in raw_classes
            ],
            level_history=basics.get("level_history", []),
            asi_history=basics.get("asi_history", []),
            feats=basics.get("feats", []),
            feat_history=basics.get("feat_history", []),
            ability_scores=dict(data.get("ability_scores", {})),
            hp_max=hp.get("max", 0),
            hp_current=hp.get("current", 0),
            hp_temp=hp.get("temp", 0),
            hp_level_history=list(hp.get("level_history", [])),
            hit_dice_str=hit_dice.get("total", "1d8"),
            hit_dice_used=hit_dice.get("used", 0),
            death_save_successes=death.get("successes", 0),
            death_save_failures=death.get("failures", 0),
            skill_proficiencies=list(profs.get("skills", [])),
            saving_throw_proficiencies=list(profs.get("saving_throws", [])),
            armor_proficiencies=list(profs.get("armor", [])),
            weapon_proficiencies=list(profs.get("weapons", [])),
            tool_proficiencies=list(profs.get("tools", [])),
            languages=list(profs.get("languages", [])),
            equipped_armor=equip.get("armor"),
            has_shield=equip.get("shield", False),
            equipped_weapons=list(equip.get("weapons", [])),
            inventory=list(equip.get("inventory", [])),
            currency=dict(equip.get("currency", {"cp": 0, "sp": 0, "ep": 0, "gp": 0, "pp": 0})),
            cantrips=list(spells.get("cantrips", [])),
            spells_known=list(spells.get("spells_known", [])),
            spell_slots_used=list(spells.get("spell_slots_used", [])),
            personality=traits.get("personality", ""),
            ideals=traits.get("ideals", ""),
            bonds=traits.get("bonds", ""),
            flaws=traits.get("flaws", ""),
            notes=data.get("notes", ""),
            conditions=list(data.get("conditions", [])),
        )

    def to_dict(self) -> dict:
        """Serialize back to the dict format used by the persistence layer."""
        return {
            "meta": {"edition": self.edition, "version": "0.1"},
            "basics": {
                "name": self.name,
                "race": self.race_index,
                "subrace": self.subrace_index,
                "class": self.primary_class_index,
                "subclass": self.classes[0].subclass if self.classes else None,
                "background": self.background_index,
                "alignment": self.alignment,
                "level": self.level,
                "experience": self.experience,
                "dragonborn_ancestry": self.dragonborn_ancestry,
                "classes": [
                    {"class_index": c.class_index, "level": c.level, "subclass": c.subclass}
                    for c in self.classes
                ],
                "level_history": self.level_history,
                "asi_history": self.asi_history,
                "feats": self.feats,
                "feat_history": self.feat_history,
            },
            "ability_scores": dict(self.ability_scores),
            "hp": {
                "max": self.hp_max,
                "current": self.hp_current,
                "temp": self.hp_temp,
                "level_history": self.hp_level_history,
            },
            "hit_dice": {"total": self.hit_dice_str, "used": self.hit_dice_used},
            "death_saves": {
                "successes": self.death_save_successes,
                "failures": self.death_save_failures,
            },
            "proficiencies": {
                "skills": self.skill_proficiencies,
                "saving_throws": self.saving_throw_proficiencies,
                "armor": self.armor_proficiencies,
                "weapons": self.weapon_proficiencies,
                "tools": self.tool_proficiencies,
                "languages": self.languages,
            },
            "equipment": {
                "armor": self.equipped_armor,
                "shield": self.has_shield,
                "weapons": self.equipped_weapons,
                "inventory": self.inventory,
                "currency": self.currency,
            },
            "spellcasting": {
                "cantrips": self.cantrips,
                "spells_known": self.spells_known,
                "spell_slots_used": self.spell_slots_used,
            } if self.cantrips or self.spells_known else None,
            "traits": {
                "personality": self.personality,
                "ideals": self.ideals,
                "bonds": self.bonds,
                "flaws": self.flaws,
            },
            "conditions": self.conditions,
            "notes": self.notes,
        }
