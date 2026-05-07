from pathlib import Path

_ICONS_ROOT = Path(__file__).parent.parent.parent.parent / "assets/icons"

_ICONS_ABILITY_ROOT = _ICONS_ROOT / "ability"
ICONS_ABILITY = {
    "STR": _ICONS_ABILITY_ROOT / "strength"    ,
    "DEX": _ICONS_ABILITY_ROOT / "dexterity"   ,
    "CON": _ICONS_ABILITY_ROOT / "constitution",
    "INT": _ICONS_ABILITY_ROOT / "intelligence",
    "WIS": _ICONS_ABILITY_ROOT / "wisdom"      ,
    "CHA": _ICONS_ABILITY_ROOT / "charisma"    ,
    }

_ICONS_ATTRIBUTE_ROOT = _ICONS_ROOT / "attribute"
ICONS_ATTRIBUTE = {
    "ac"           : _ICONS_ATTRIBUTE_ROOT / "ac"           ,
    "attunement"   : _ICONS_ATTRIBUTE_ROOT / "attunement"   ,
    "bonus"        : _ICONS_ATTRIBUTE_ROOT / "bonus"        ,
    "light"        : _ICONS_ATTRIBUTE_ROOT / "light"        ,
    "penalty"      : _ICONS_ATTRIBUTE_ROOT / "penalty"      ,
    "range"        : _ICONS_ATTRIBUTE_ROOT / "range"        ,
    "saving-throw" : _ICONS_ATTRIBUTE_ROOT / "saving-throw" ,
    "skillcheck"   : _ICONS_ATTRIBUTE_ROOT / "skillcheck"   ,
    "terrain"      : _ICONS_ATTRIBUTE_ROOT / "terrain"      ,
    "test"         : _ICONS_ATTRIBUTE_ROOT / "test"         ,
    "vision"       : _ICONS_ATTRIBUTE_ROOT / "vision"       ,
}

_ICONS_CAMPAIGN_ROOT = _ICONS_ROOT / "campaign"
ICONS_CAMPAIGN = {
    "candlekeep"               : _ICONS_CAMPAIGN_ROOT / "candlekeep"               ,
    "curse-of-strahd"          : _ICONS_CAMPAIGN_ROOT / "curse-of-strahd"          ,
    "descent-into-avernus"     : _ICONS_CAMPAIGN_ROOT / "descent-into-avernus"     ,
    "elemental-evil"           : _ICONS_CAMPAIGN_ROOT / "elemental-evil"           ,
    "hoard-of-the-dragon-queen": _ICONS_CAMPAIGN_ROOT / "hoard-of-the-dragon-queen",
    "light-of-xaryxis"         : _ICONS_CAMPAIGN_ROOT / "light-of-xaryxis"         ,
    "out-of-the-abyss"         : _ICONS_CAMPAIGN_ROOT / "out-of-the-abyss"         ,
    "rime-of-the-frostmaiden"  : _ICONS_CAMPAIGN_ROOT / "rime-of-the-frostmaiden"  ,
    "storm-kings-thunder"      : _ICONS_CAMPAIGN_ROOT / "storm-kings-thunder"      ,
    "tomb-of-annihilation"     : _ICONS_CAMPAIGN_ROOT / "tomb-of-annihilation"     ,
    "waterdeep"                : _ICONS_CAMPAIGN_ROOT / "waterdeep"                ,
    "yawning-portal"           : _ICONS_CAMPAIGN_ROOT / "yawning-portal"           ,
}

_ICONS_CLASS_ROOT = _ICONS_ROOT / "class"
ICONS_CLASS = {
    "artificer": _ICONS_CLASS_ROOT / "artificer",
    "barbarian": _ICONS_CLASS_ROOT / "barbarian",
    "bard"     : _ICONS_CLASS_ROOT / "bard"     ,
    "cleric"   : _ICONS_CLASS_ROOT / "cleric"   ,
    "druid"    : _ICONS_CLASS_ROOT / "druid"    ,
    "fighter"  : _ICONS_CLASS_ROOT / "fighter"  ,
    "monk"     : _ICONS_CLASS_ROOT / "monk"     ,
    "paladin"  : _ICONS_CLASS_ROOT / "paladin"  ,
    "ranger"   : _ICONS_CLASS_ROOT / "ranger"   ,
    "rogue"    : _ICONS_CLASS_ROOT / "rogue"    ,
    "sorcerer" : _ICONS_CLASS_ROOT / "sorcerer" ,
    "warlock"  : _ICONS_CLASS_ROOT / "warlock"  ,
    "wizard"   : _ICONS_CLASS_ROOT / "wizard"   ,
}

_ICONS_COMBAT_ROOT = _ICONS_ROOT / "combat"
ICONS_COMBAT = {
    "action"      : _ICONS_COMBAT_ROOT / "action"      ,
    "bonus-action": _ICONS_COMBAT_ROOT / "bonus-action",
    "initiative"  : _ICONS_COMBAT_ROOT / "initiative"  ,
    "melee"       : _ICONS_COMBAT_ROOT / "melee"       ,
    "ranged"      : _ICONS_COMBAT_ROOT / "ranged"      ,
    "reach"       : _ICONS_COMBAT_ROOT / "reach"       ,
    "reaction"    : _ICONS_COMBAT_ROOT / "reaction"    ,
    "round"       : _ICONS_COMBAT_ROOT / "round"       ,
    "target"      : _ICONS_COMBAT_ROOT / "target"      ,
}

_ICONS_CONDITION_ROOT = _ICONS_ROOT / "condition"
ICONS_CONDITION = {
    "blinded"      : _ICONS_CONDITION_ROOT / "blinded"      ,
    "charmed"      : _ICONS_CONDITION_ROOT / "charmed"      ,
    "deafened"     : _ICONS_CONDITION_ROOT / "deafened"     ,
    "exhaustion"   : _ICONS_CONDITION_ROOT / "exhaustion"   ,
    "frightened"   : _ICONS_CONDITION_ROOT / "frightened"   ,
    "grappled"     : _ICONS_CONDITION_ROOT / "grappled"     ,
    "incapacitated": _ICONS_CONDITION_ROOT / "incapacitated",
    "invisible"    : _ICONS_CONDITION_ROOT / "invisible"    ,
    "paralyzed"    : _ICONS_CONDITION_ROOT / "paralyzed"    ,
    "petrified"    : _ICONS_CONDITION_ROOT / "petrified"    ,
    "poisoned"     : _ICONS_CONDITION_ROOT / "poisoned"     ,
    "prone"        : _ICONS_CONDITION_ROOT / "prone"        ,
    "restrained"   : _ICONS_CONDITION_ROOT / "restrained"   ,
    "silenced"     : _ICONS_CONDITION_ROOT / "silenced"     ,
    "sleep"        : _ICONS_CONDITION_ROOT / "sleep"        ,
    "stunned"      : _ICONS_CONDITION_ROOT / "stunned"      ,
    "unconscious"  : _ICONS_CONDITION_ROOT / "unconscious"  ,
}

_ICONS_D20TEST_ROOT = _ICONS_ROOT / "d20test"
ICONS_D20TEST = {
    "attacked"    : _ICONS_D20TEST_ROOT / "attacked"    ,
    "attacking"   : _ICONS_D20TEST_ROOT / "attacking"   ,
    "saving-throw": _ICONS_D20TEST_ROOT / "saving-throw",
}

_ICONS_DAMAGE_ROOT = _ICONS_ROOT / "damage"
ICONS_DAMAGE = {
    "acid"         : _ICONS_DAMAGE_ROOT / "acid"         ,
    "bludgeoning"  : _ICONS_DAMAGE_ROOT / "bludgeoning"  ,
    "cold"         : _ICONS_DAMAGE_ROOT / "cold"         ,
    "fire"         : _ICONS_DAMAGE_ROOT / "fire"         ,
    "force"        : _ICONS_DAMAGE_ROOT / "force"        ,
    "immunity"     : _ICONS_DAMAGE_ROOT / "immunity"     ,
    "lightning"    : _ICONS_DAMAGE_ROOT / "lightning"    ,
    "necrotic"     : _ICONS_DAMAGE_ROOT / "necrotic"     ,
    "piercing"     : _ICONS_DAMAGE_ROOT / "piercing"     ,
    "poison"       : _ICONS_DAMAGE_ROOT / "poison"       ,
    "psychic"      : _ICONS_DAMAGE_ROOT / "psychic"      ,
    "radiant"      : _ICONS_DAMAGE_ROOT / "radiant"      ,
    "resistance"   : _ICONS_DAMAGE_ROOT / "resistance"   ,
    "slashing"     : _ICONS_DAMAGE_ROOT / "slashing"     ,
    "thunder"      : _ICONS_DAMAGE_ROOT / "thunder"      ,
    "vulnerability": _ICONS_DAMAGE_ROOT / "vulnerability",
}

_ICONS_DICE_ROOT = _ICONS_ROOT / "dice"
ICONS_DICE = {
    "advantage"   : _ICONS_DICE_ROOT / "advantage"   ,
    "d4"          : _ICONS_DICE_ROOT / "d4"          ,
    "d6"          : _ICONS_DICE_ROOT / "d6"          ,
    "d8"          : _ICONS_DICE_ROOT / "d8"          ,
    "d10"         : _ICONS_DICE_ROOT / "d10"         ,
    "d12"         : _ICONS_DICE_ROOT / "d12"         ,
    "d20"         : _ICONS_DICE_ROOT / "d20"         ,
    "disadvantage": _ICONS_DICE_ROOT / "disadvantage",
    "roll"        : _ICONS_DICE_ROOT / "roll"        ,
}

_ICONS_ENTITY_ROOT = _ICONS_ROOT / "entity"
ICONS_ENTITY = {
    "archive"     : _ICONS_ENTITY_ROOT / "archive"     ,
    "armor"       : _ICONS_ENTITY_ROOT / "armor"       ,
    "book"        : _ICONS_ENTITY_ROOT / "book"        ,
    "location"    : _ICONS_ENTITY_ROOT / "location"    ,
    "loot"        : _ICONS_ENTITY_ROOT / "loot"        ,
    "magic-item"  : _ICONS_ENTITY_ROOT / "magic-item"  ,
    "map"         : _ICONS_ENTITY_ROOT / "map"         ,
    "mount"       : _ICONS_ENTITY_ROOT / "mount"       ,
    "object"      : _ICONS_ENTITY_ROOT / "object"      ,
    "organization": _ICONS_ENTITY_ROOT / "organization",
    "pack"        : _ICONS_ENTITY_ROOT / "pack"        ,
    "person"      : _ICONS_ENTITY_ROOT / "person"      ,
    "pet"         : _ICONS_ENTITY_ROOT / "pet"         ,
    "potion"      : _ICONS_ENTITY_ROOT / "potion"      ,
    "ring"        : _ICONS_ENTITY_ROOT / "ring"        ,
    "scroll"      : _ICONS_ENTITY_ROOT / "scroll"      ,
    "ship"        : _ICONS_ENTITY_ROOT / "ship"        ,
    "spellbook"   : _ICONS_ENTITY_ROOT / "spellbook"   ,
    "summon"      : _ICONS_ENTITY_ROOT / "summon"      ,
    "time"        : _ICONS_ENTITY_ROOT / "time"        ,
    "tool"        : _ICONS_ENTITY_ROOT / "tool"        ,
    "trinket"     : _ICONS_ENTITY_ROOT / "trinket"     ,
    "vehicle"     : _ICONS_ENTITY_ROOT / "vehicle"     ,
    "wand"        : _ICONS_ENTITY_ROOT / "wand"        ,
    "weapon"      : _ICONS_ENTITY_ROOT / "weapon"      ,
    "world"       : _ICONS_ENTITY_ROOT / "world"       ,
}

_ICONS_GAME_ROOT = _ICONS_ROOT / "game"
ICONS_GAME = {
    "adventure-book": _ICONS_GAME_ROOT / "adventure-book",
    "campaign"      : _ICONS_GAME_ROOT / "campaign"      ,
    "character"     : _ICONS_GAME_ROOT / "character"     ,
    "combat"        : _ICONS_GAME_ROOT / "combat"        ,
    "concentration" : _ICONS_GAME_ROOT / "concentration" ,
    "dm"            : _ICONS_GAME_ROOT / "dm"            ,
    "explore"       : _ICONS_GAME_ROOT / "explore"       ,
    "hazard"        : _ICONS_GAME_ROOT / "hazard"        ,
    "inspiration"   : _ICONS_GAME_ROOT / "inspiration"   ,
    "lock"          : _ICONS_GAME_ROOT / "lock"          ,
    "monster"       : _ICONS_GAME_ROOT / "monster"       ,
    "party"         : _ICONS_GAME_ROOT / "party"         ,
    "puzzle"        : _ICONS_GAME_ROOT / "puzzle"        ,
    "rest"          : _ICONS_GAME_ROOT / "rest"          ,
    "social"        : _ICONS_GAME_ROOT / "social"        ,
    "source-book"   : _ICONS_GAME_ROOT / "source-book"   ,
    "spell"         : _ICONS_GAME_ROOT / "spell"         ,
    "trap"          : _ICONS_GAME_ROOT / "trap"          ,
}

_ICONS_HP_ROOT = _ICONS_ROOT / "hp"
ICONS_HP = {
    "blood": _ICONS_HP_ROOT / "blood",
    "empty": _ICONS_HP_ROOT / "empty",
    "full" : _ICONS_HP_ROOT / "full" ,
    "half" : _ICONS_HP_ROOT / "half" ,
    "temp" : _ICONS_HP_ROOT / "temp" ,
}

_ICONS_LOCATION_ROOT = _ICONS_ROOT / "location"
ICONS_LOCATION = {
    "bastion" : _ICONS_LOCATION_ROOT / "bastion" ,
    "camp"    : _ICONS_LOCATION_ROOT / "camp"    ,
    "castle"  : _ICONS_LOCATION_ROOT / "castle"  ,
    "dungeon" : _ICONS_LOCATION_ROOT / "dungeon" ,
    "forest"  : _ICONS_LOCATION_ROOT / "forest"  ,
    "hut"     : _ICONS_LOCATION_ROOT / "hut"     ,
    "mountain": _ICONS_LOCATION_ROOT / "mountain",
    "portal"  : _ICONS_LOCATION_ROOT / "portal"  ,
    "tavern"  : _ICONS_LOCATION_ROOT / "tavern"  ,
    "tower"   : _ICONS_LOCATION_ROOT / "tower"   ,
    "village" : _ICONS_LOCATION_ROOT / "village" ,
}

_ICONS_LOGO_ROOT = _ICONS_ROOT / "logo"
ICONS_LOGO = {
    "adventurers-league": _ICONS_LOGO_ROOT / "adventurers-league",
    "critical-role"     : _ICONS_LOGO_ROOT / "critical-role"     ,
    "dnd-beyond"        : _ICONS_LOGO_ROOT / "dnd-beyond"        ,
    "dnd"               : _ICONS_LOGO_ROOT / "dnd"               ,
    "fantasy-grounds"   : _ICONS_LOGO_ROOT / "fantasy-grounds"   ,
    "foundry"           : _ICONS_LOGO_ROOT / "foundry"           ,
    "owlbear-rodeo"     : _ICONS_LOGO_ROOT / "owlbear-rodeo"     ,
    "roll20"            : _ICONS_LOGO_ROOT / "roll20"            ,
    "tiddlywiki"        : _ICONS_LOGO_ROOT / "tiddlywiki"        ,
}

_ICONS_MONSTER_ROOT = _ICONS_ROOT / "monster"
ICONS_MONSTER = {
    "aberration" : _ICONS_MONSTER_ROOT / "aberration" ,
    "beast"      : _ICONS_MONSTER_ROOT / "beast"      ,
    "celestial"  : _ICONS_MONSTER_ROOT / "celestial"  ,
    "construct"  : _ICONS_MONSTER_ROOT / "construct"  ,
    "dragon"     : _ICONS_MONSTER_ROOT / "dragon"     ,
    "elemental"  : _ICONS_MONSTER_ROOT / "elemental"  ,
    "fae"        : _ICONS_MONSTER_ROOT / "fae"        ,
    "fiend"      : _ICONS_MONSTER_ROOT / "fiend"      ,
    "giant"      : _ICONS_MONSTER_ROOT / "giant"      ,
    "humanoid"   : _ICONS_MONSTER_ROOT / "humanoid"   ,
    "monstrosity": _ICONS_MONSTER_ROOT / "monstrosity",
    "ooze"       : _ICONS_MONSTER_ROOT / "ooze"       ,
    "plant"      : _ICONS_MONSTER_ROOT / "plant"      ,
    "undead"     : _ICONS_MONSTER_ROOT / "undead"     ,
}

_ICONS_MOVEMENT_ROOT = _ICONS_ROOT / "movement"
ICONS_MOVEMENT = {
    "burrowing": _ICONS_MOVEMENT_ROOT / "burrowing",
    "climbing" : _ICONS_MOVEMENT_ROOT / "climbing" ,
    "flying"   : _ICONS_MOVEMENT_ROOT / "flying"   ,
    "swimming" : _ICONS_MOVEMENT_ROOT / "swimming" ,
    "walking"  : _ICONS_MOVEMENT_ROOT / "walking"  ,
}

_ICONS_PROFICIENCY_ROOT = _ICONS_ROOT / "proficiency"
ICONS_PROFICIENCY = {
    "expertise" : _ICONS_PROFICIENCY_ROOT / "expertise" ,
    "half"      : _ICONS_PROFICIENCY_ROOT / "half"      ,
    "proficient": _ICONS_PROFICIENCY_ROOT / "proficient",
    "unskilled" : _ICONS_PROFICIENCY_ROOT / "unskilled" ,
}

_ICONS_ROLL20_ROOT = _ICONS_ROOT / "roll20"
ICONS_ROLL20 = {
    "advantage"      : _ICONS_ROLL20_ROOT / "advantage"      ,
    "attacked-adv"   : _ICONS_ROLL20_ROOT / "attacked-adv"   ,
    "attacked-dis"   : _ICONS_ROLL20_ROOT / "attacked-dis"   ,
    "attacking-adv"  : _ICONS_ROLL20_ROOT / "attacking-adv"  ,
    "attacking-dis"  : _ICONS_ROLL20_ROOT / "attacking-dis"  ,
    "blinded"        : _ICONS_ROLL20_ROOT / "blinded"        ,
    "bloodied"       : _ICONS_ROLL20_ROOT / "bloodied"       ,
    "burrowing"      : _ICONS_ROLL20_ROOT / "burrowing"      ,
    "charmed"        : _ICONS_ROLL20_ROOT / "charmed"        ,
    "climbing"       : _ICONS_ROLL20_ROOT / "climbing"       ,
    "concentration-1": _ICONS_ROLL20_ROOT / "concentration-1",
    "concentration-2": _ICONS_ROLL20_ROOT / "concentration-2",
    "deafened"       : _ICONS_ROLL20_ROOT / "deafened"       ,
    "disadvantage"   : _ICONS_ROLL20_ROOT / "disadvantage"   ,
    "flying"         : _ICONS_ROLL20_ROOT / "flying"         ,
    "frightened"     : _ICONS_ROLL20_ROOT / "frightened"     ,
    "grappled"       : _ICONS_ROLL20_ROOT / "grappled"       ,
    "incapacitated"  : _ICONS_ROLL20_ROOT / "incapacitated"  ,
    "invisible"      : _ICONS_ROLL20_ROOT / "invisible"      ,
    "paralyzed"      : _ICONS_ROLL20_ROOT / "paralyzed"      ,
    "petrified"      : _ICONS_ROLL20_ROOT / "petrified"      ,
    "poisoned"       : _ICONS_ROLL20_ROOT / "poisoned"       ,
    "prone"          : _ICONS_ROLL20_ROOT / "prone"          ,
    "restrained"     : _ICONS_ROLL20_ROOT / "restrained"     ,
    "saving-adv"     : _ICONS_ROLL20_ROOT / "saving-adv"     ,
    "saving-dis"     : _ICONS_ROLL20_ROOT / "saving-dis"     ,
    "silenced"       : _ICONS_ROLL20_ROOT / "silenced"       ,
    "sleep"          : _ICONS_ROLL20_ROOT / "sleep"          ,
    "stunned"        : _ICONS_ROLL20_ROOT / "stunned"        ,
    "swimming"       : _ICONS_ROLL20_ROOT / "swimming"       ,
    "unconscious"    : _ICONS_ROLL20_ROOT / "unconscious"    ,
    "walking"        : _ICONS_ROLL20_ROOT / "walking"        ,
}

_ICONS_SKILL_ROOT = _ICONS_ROOT / "skill"
ICONS_SKILL = {
    "Acrobatics"     : _ICONS_SKILL_ROOT / "acrobatics"     ,
    "Animal Handling": _ICONS_SKILL_ROOT / "animal-handling",
    "Arcana"         : _ICONS_SKILL_ROOT / "arcana"         ,
    "Athletics"      : _ICONS_SKILL_ROOT / "athletics"      ,
    "Deception"      : _ICONS_SKILL_ROOT / "deception"      ,
    "History"        : _ICONS_SKILL_ROOT / "history"        ,
    "Insight"        : _ICONS_SKILL_ROOT / "insight"        ,
    "Intimidation"   : _ICONS_SKILL_ROOT / "intimidation"   ,
    "Investigation"  : _ICONS_SKILL_ROOT / "investigation"  ,
    "Medicine"       : _ICONS_SKILL_ROOT / "medicine"       ,
    "Nature"         : _ICONS_SKILL_ROOT / "nature"         ,
    "Perception"     : _ICONS_SKILL_ROOT / "perception"     ,
    "Performance"    : _ICONS_SKILL_ROOT / "performance"    ,
    "Persuasion"     : _ICONS_SKILL_ROOT / "persuasion"     ,
    "Religion"       : _ICONS_SKILL_ROOT / "religion"       ,
    "Sleight of Hand": _ICONS_SKILL_ROOT / "sleight-of-hand",
    "Stealth"        : _ICONS_SKILL_ROOT / "stealth"        ,
    "Survival"       : _ICONS_SKILL_ROOT / "survival"       ,
}

_ICONS_SLOT_ROOT = _ICONS_ROOT / "slot"
ICONS_SLOT = {
    "1-0": _ICONS_SLOT_ROOT / "slot-1-0",
    "1-1": _ICONS_SLOT_ROOT / "slot-1-1",
    "2-0": _ICONS_SLOT_ROOT / "slot-2-0",
    "2-1": _ICONS_SLOT_ROOT / "slot-2-1",
    "2-2": _ICONS_SLOT_ROOT / "slot-2-2",
    "3-0": _ICONS_SLOT_ROOT / "slot-3-0",
    "3-1": _ICONS_SLOT_ROOT / "slot-3-1",
    "3-2": _ICONS_SLOT_ROOT / "slot-3-2",
    "3-3": _ICONS_SLOT_ROOT / "slot-3-3",
    "4-0": _ICONS_SLOT_ROOT / "slot-4-0",
    "4-1": _ICONS_SLOT_ROOT / "slot-4-1",
    "4-2": _ICONS_SLOT_ROOT / "slot-4-2",
    "4-3": _ICONS_SLOT_ROOT / "slot-4-3",
    "4-4": _ICONS_SLOT_ROOT / "slot-4-4",
}

_ICONS_SPELL_ROOT = _ICONS_ROOT / "spell"
ICONS_SPELL = {
    "abjuration"   : _ICONS_SPELL_ROOT / "abjuration"   ,
    "concentration": _ICONS_SPELL_ROOT / "concentration",
    "conjuration"  : _ICONS_SPELL_ROOT / "conjuration"  ,
    "consumed"     : _ICONS_SPELL_ROOT / "consumed"     ,
    "cost"         : _ICONS_SPELL_ROOT / "cost"         ,
    "divination"   : _ICONS_SPELL_ROOT / "divination"   ,
    "enchantment"  : _ICONS_SPELL_ROOT / "enchantment"  ,
    "evocation"    : _ICONS_SPELL_ROOT / "evocation"    ,
    "illusion"     : _ICONS_SPELL_ROOT / "illusion"     ,
    "instantaneous": _ICONS_SPELL_ROOT / "instantaneous",
    "material"     : _ICONS_SPELL_ROOT / "material"     ,
    "necromancy"   : _ICONS_SPELL_ROOT / "necromancy"   ,
    "octagon"      : _ICONS_SPELL_ROOT / "octagon"      ,
    "ritual"       : _ICONS_SPELL_ROOT / "ritual"       ,
    "somatic"      : _ICONS_SPELL_ROOT / "somatic"      ,
    "transmutation": _ICONS_SPELL_ROOT / "transmutation",
    "upcast"       : _ICONS_SPELL_ROOT / "upcast"       ,
    "vocal"        : _ICONS_SPELL_ROOT / "vocal"        ,
}

_ICONS_TARGET_ROOT = _ICONS_ROOT / "target"
ICONS_TARGET = {
    "circle"   : _ICONS_TARGET_ROOT / "circle"   ,
    "cone"     : _ICONS_TARGET_ROOT / "cone"      ,
    "cube"     : _ICONS_TARGET_ROOT / "cube"      ,
    "cylinder" : _ICONS_TARGET_ROOT / "cylinder"  ,
    "emanation": _ICONS_TARGET_ROOT / "emanation" ,
    "line"     : _ICONS_TARGET_ROOT / "line"      ,
    "self"     : _ICONS_TARGET_ROOT / "self"      ,
    "sphere"   : _ICONS_TARGET_ROOT / "sphere"    ,
    "square"   : _ICONS_TARGET_ROOT / "square"    ,
    "touch"    : _ICONS_TARGET_ROOT / "touch"     ,
    "wall"     : _ICONS_TARGET_ROOT / "wall"      ,
}

_ICONS_UTIL_ROOT = _ICONS_ROOT / "util"
ICONS_UTIL = {
    "bubble"        : _ICONS_UTIL_ROOT / "bubble"        ,
    "build"         : _ICONS_UTIL_ROOT / "build"         ,
    "cog"           : _ICONS_UTIL_ROOT / "cog"           ,
    "cross"         : _ICONS_UTIL_ROOT / "cross"         ,
    "home"          : _ICONS_UTIL_ROOT / "home"          ,
    "not-applicable": _ICONS_UTIL_ROOT / "not-applicable",
    "search"        : _ICONS_UTIL_ROOT / "search"        ,
    "star"          : _ICONS_UTIL_ROOT / "star"          ,
    "tick"          : _ICONS_UTIL_ROOT / "tick"          ,
    "trade"         : _ICONS_UTIL_ROOT / "trade"         ,
}

_ICONS_WEAPON_ROOT = _ICONS_ROOT / "weapon"
ICONS_WEAPON = {
    "arrow"      : _ICONS_WEAPON_ROOT / "arrow"      ,
    "battleaxe"  : _ICONS_WEAPON_ROOT / "battleaxe"  ,
    "bow"        : _ICONS_WEAPON_ROOT / "bow"        ,
    "club"       : _ICONS_WEAPON_ROOT / "club"       ,
    "crossbow"   : _ICONS_WEAPON_ROOT / "crossbow"   ,
    "dagger"     : _ICONS_WEAPON_ROOT / "dagger"     ,
    "flail"      : _ICONS_WEAPON_ROOT / "flail"      ,
    "glaive"     : _ICONS_WEAPON_ROOT / "glaive"     ,
    "halberd"    : _ICONS_WEAPON_ROOT / "halberd"    ,
    "hammer"     : _ICONS_WEAPON_ROOT / "hammer"     ,
    "handaxe"    : _ICONS_WEAPON_ROOT / "handaxe"    ,
    "lance"      : _ICONS_WEAPON_ROOT / "lance"      ,
    "mace"       : _ICONS_WEAPON_ROOT / "mace"       ,
    "morningstar": _ICONS_WEAPON_ROOT / "morningstar",
    "musket"     : _ICONS_WEAPON_ROOT / "musket"     ,
    "pike"       : _ICONS_WEAPON_ROOT / "pike"       ,
    "pistol"     : _ICONS_WEAPON_ROOT / "pistol"     ,
    "rapier"     : _ICONS_WEAPON_ROOT / "rapier"     ,
    "scimitar"   : _ICONS_WEAPON_ROOT / "scimitar"   ,
    "sickle"     : _ICONS_WEAPON_ROOT / "sickle"     ,
    "sling"      : _ICONS_WEAPON_ROOT / "sling"      ,
    "spear"      : _ICONS_WEAPON_ROOT / "spear"      ,
    "staff"      : _ICONS_WEAPON_ROOT / "staff"      ,
    "strike"     : _ICONS_WEAPON_ROOT / "strike"     ,
    "sword"      : _ICONS_WEAPON_ROOT / "sword"      ,
    "trident"    : _ICONS_WEAPON_ROOT / "trident"    ,
    "whip"       : _ICONS_WEAPON_ROOT / "whip"       ,
}


_MAPS_ROOT   = Path(__file__).parent.parent.parent.parent / "assets/maps"
_TOKENS_ROOT = Path(__file__).parent.parent.parent.parent / "assets/tokens"


def resolve(p) -> str:
    """Return the icon path as a string with .svg extension, for use with QIcon."""
    s = str(p)
    return s if s.endswith(".svg") else s + ".svg"


# ── SVG recoloring ─────────────────────────────────────────────────────────

import re as _re


def _patch_svg_color(svg_text: str, color: str) -> str:
    """Return *svg_text* with fill colors replaced by *color*.

    Injects fill on the root <svg> element (so all child paths inherit it) and
    also replaces any explicit black fills (#000000 / #000 / black) in child
    elements.  Stroke colors are intentionally left untouched.
    """
    def _patch_root(m: _re.Match) -> str:
        body, close = m.group(1), m.group(2)
        if _re.search(r'\bfill=', body):
            body = _re.sub(r'\bfill="[^"]*"', f'fill="{color}"', body)
            body = _re.sub(r"\bfill='[^']*'", f"fill='{color}'", body)
        else:
            body += f' fill="{color}"'
        return f"<svg{body}{close}"

    patched = _re.sub(r'<svg([^>]*?)(/>|>)', _patch_root, svg_text, count=1)

    for _black in ("#000000", "#000", "black"):
        patched = patched.replace(f'fill="{_black}"', f'fill="{color}"')
        patched = patched.replace(f"fill='{_black}'", f"fill='{color}'")

    return patched


def recolored_icon(path, color: str = "#ffffff"):
    """Load an SVG icon and replace its fill color before rendering.

    Args:
        path: Path object or string accepted by ``resolve()``.
        color: CSS color string, e.g. ``"#ffffff"``, ``"#c8a96e"``, ``"white"``.

    Returns:
        ``QIcon`` — scaleable via ``.pixmap(w, h)`` as usual.

    Example::

        lbl.setPixmap(assets.recolored_icon(assets.ICONS_CLASS["barbarian"]).pixmap(32, 32))
        btn.setIcon(assets.recolored_icon(assets.ICONS_UTIL["star"], "#c8a96e"))
    """
    from PySide6.QtSvg import QSvgRenderer
    from PySide6.QtGui import QIcon, QPixmap, QPainter
    from PySide6.QtCore import Qt

    with open(resolve(path), encoding="utf-8") as f:
        content = f.read()

    content = _patch_svg_color(content, color)

    renderer = QSvgRenderer(content.encode("utf-8"))
    sz = renderer.defaultSize()
    px = QPixmap(sz.width(), sz.height())
    px.fill(Qt.GlobalColor.transparent)
    painter = QPainter(px)
    renderer.render(painter)
    painter.end()
    return QIcon(px)
