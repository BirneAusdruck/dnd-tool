from __future__ import annotations
from enum import Enum
from typing import TypeAlias

class SRDConstants:
    ABILITIES: list[dict] = [
        {"index": "strength",     "name": "Strength",     "short": "STR"}, 
        {"index": "dexterity",    "name": "Dexterity",    "short": "DEX"}, 
        {"index": "constitution", "name": "Constitution", "short": "CON"}, 
        {"index": "intelligence", "name": "Intelligence", "short": "INT"}, 
        {"index": "wisdom",       "name": "Wisdom",       "short": "WIS"}, 
        {"index": "charisma",     "name": "Charisma",     "short": "CHA"}
    ]

    SKILLS: list[dict] = [
        {"index": "acrobatics",      "name": "Acrobatics",      "ability": "DEX"},
        {"index": "animal_handling", "name": "Animal Handling", "ability": "WIS"},
        {"index": "arcana",          "name": "Arcana",          "ability": "INT"},
        {"index": "athletics",       "name": "Athletics",       "ability": "STR"},
        {"index": "deception",       "name": "Deception",       "ability": "CHA"},
        {"index": "history",         "name": "History",         "ability": "INT"},
        {"index": "insight",         "name": "Insight",         "ability": "WIS"},
        {"index": "intimidation",    "name": "Intimidation",    "ability": "CHA"},
        {"index": "investigation",   "name": "Investigation",   "ability": "INT"},
        {"index": "medicine",         "name": "Medicine",        "ability": "WIS"},
        {"index": "nature",          "name": "Nature",          "ability": "INT"},
        {"index": "perception",      "name": "Perception",      "ability": "WIS"},
        {"index": "performance",     "name": "Performance",     "ability": "CHA"},
        {"index": "persuasion",      "name": "Persuasion",      "ability": "CHA"},
        {"index": "religion",        "name": "Religion",        "ability": "INT"},
        {"index": "sleight_of_hand", "name": "Sleight of Hand", "ability": "DEX"},
        {"index": "stealth",         "name": "Stealth",         "ability": "DEX"},
        {"index": "survival",        "name": "Survival",        "ability": "WIS"},
    ]

    ALIGNMENTS: list[dict[str, str]] = [
        {"index": "lawful_good",     "name": "Lawful Good"    }, 
        {"index": "neutral_good",    "name": "Neutral Good"   }, 
        {"index": "chaotic_good",    "name": "Chaotic Good"   },
        {"index": "lawful_neutral",  "name": "Lawful Neutral" }, 
        {"index": "true_neutral",    "name": "True Neutral"   }, 
        {"index": "chaotic_neutral", "name": "Chaotic Neutral"},
        {"index": "lawful_evil",     "name": "Lawful Evil"    }, 
        {"index": "neutral_evil",    "name": "Neutral Evil"   }, 
        {"index": "chaotic_evil",    "name": "Chaotic Evil"   },
    ]

class HpStat(str, Enum):
    HP      = "hp"
    MAX_HP  = "max_hp"
    TEMP_HP = "temp_hp"
    
class CombatStat(str, Enum):
    ARMOR_CLASS               = "armor_class"
    INITIATIVE                = "initiative"
    SPEED                     = "speed"
    SPELL_DIFFICULTY_CLASS    = "spell_difficulty_class"
    PROFICIENCY               = "proficiency"
    SAVING_THROWS_ALL         = "saving_throws_all"


class AttackType(str, Enum):
    MELEE_DAMAGE   = "melee_damage"
    RANGED_DAMAGE  = "ranged_damage"
    SPELL_DAMAGE   = "spell_damage"

class ResourceStat(str, Enum):
    RAGE_USES                = "rage_uses"
    SPELL_SLOTS              = "spell_slots"
    HIT_DICE                 = "hit_dice"
    BARDIC_INSPIRATION_USES  = "bardic_inspiration_uses"
    INNATE_SORCERY_USES      = "innate_sorcery_uses"

class AbilityCheck(str, Enum):
    STRENGTH_CHECK          = "STR_check"
    DEXTERITY_CHECK         = "DEX_check"
    CONSTITUTION_CHECK      = "CON_check"
    INTELLIGENCE_CHECK      = "INT_check"
    WISDOM_CHECK            = "WIS_check"
    CHARISMA_CHECK          = "CHA_check"

class AbilitySavingThrow(str, Enum):
    STRENGTH_SAVING_THROW           = "STR_saving_throw"
    DEXTERITY_SAVING_THROW          = "DEX_saving_throw"
    CONSTITUTION_SAVING_THROW       = "CON_saving_throw"
    INTELLIGENCE_SAVING_THROW       = "INT_saving_throw"
    WISDOM_SAVING_THROW             = "WIS_saving_throw"
    CHARISMA_SAVING_THROW           = "CHA_saving_throw"


class Alignment(str, Enum):
    LAWFUL_GOOD     = "lawful_good"      
    NEUTRAL_GOOD    = "neutral_good"     
    CHAOTIC_GOOD    = "chaotic_good"   
    LAWFUL_NEUTRAL  = "lawful_neutral"   
    TRUE_NEUTRAL    = "true_neutral"   
    CHAOTIC_NEUTRAL = "chaotic_neutral" 
    LAWFUL_EVIL     = "lawful_evil"      
    NEUTRAL_EVIL    = "neutral_evil"     
    CHAOTIC_EVIL    = "chaotic_evil"

class ShortAbility(str, Enum):
    STR = "STR"  
    DEX = "DEX" 
    CON = "CON" 
    INT = "INT" 
    WIS = "WIS" 
    CHA = "CHA"


class Ability(str, Enum):
    STRENGTH     = "strength"  
    DEXTERITY    = "dexterity" 
    CONSTITUTION = "constitution" 
    INTELLIGENCE = "intelligence" 
    WISDOM       = "wisdom" 
    CHARISMA     = "charisma"

class Skill(str, Enum):
    ACROBATICS      = "acrobatics"     
    ANIMAL_HANDLING = "animal_handling"
    ARCANA          = "arcana"         
    ATHLETICS       = "athletics"      
    DECEPTION       = "deception"      
    HISTORY         = "history"        
    INSIGHT         = "insight"        
    INTIMIDATION    = "intimidation"   
    INVESTIGATION   = "investigation"  
    MEDICINE         = "medicine"        
    NATURE          = "nature"      
    PERCEPTION      = "perception"     
    PERFORMANCE     = "performance"    
    PERSUASION      = "persuasion"     
    RELIGION        = "religion"       
    SLEIGHT_OF_HAND = "sleight_of_hand"
    STEALTH         = "stealth"        
    SURVIVAL        = "survival"

class ItemKind(str, Enum):
    WEAPON     = "weapon"
    ARMOR      = "armor"
    EQUIPMENT  = "equipment"
    MAGIC_ITEM = "magic_item"


class WeaponProperty(str, Enum):
    AMMUNITION  = "ammunition"
    FINESSE     = "finesse"
    HEAVY       = "heavy"
    LIGHT       = "light"
    LOADING     = "loading"
    RANGE       = "range"
    REACH       = "reach"
    SPECIAL     = "special"
    THROWN      = "thrown"
    TWO_HANDED  = "two_handed"
    VERSATILE   = "versatile"


class WeaponMastery(str, Enum):
    CLEAVE = "cleave"
    GRAZE  = "graze"
    NICK   = "nick"
    PUSH   = "push"
    SAP    = "sap"
    SLOW   = "slow"
    TOPPLE = "topple"
    VEX    = "vex"


class MagicItemRarity(str, Enum):
    COMMON    = "common"
    UNCOMMON  = "uncommon"
    RARE      = "rare"
    VERY_RARE = "very_rare"
    LEGENDARY = "legendary"
    ARTIFACT  = "artifact"


class WeaponCategory(str, Enum):
    SIMPLE_MELEE = "simple_melee"
    SIMPLE_RANGED = "simple_ranged"
    MARTIAL_MELEE = "martial_melee"
    MARTIAL_RANGED = "martial_ranged"

class ArmorCategory(str, Enum):
    CLOTH = "cloth" 
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"
    SHIELD = "shield"

class EquipmentCategory(str, Enum):
    ADVENTURING_GEAR = "adventuring_gear"
    AMMUNITION = "ammunition"
    ARCANE_FOCUS = "arcane_focus"
    DRUIDIC_FOCUS = "druidic_focus"
    HOLY_SYMBOL = "holy_symbol"
    TOOL = "tool"
    PACK = "pack"

class MagicItemCategory(str, Enum):
    POTION = "potion" 
    MAGIC_WEAPON = "magic_weapon" 
    MAGIC_ARMOR = "magic_armor" 
    WONDROUS = "wondrous"
    RING = "ring"
    ROD = "rod"
    STAFF = "staff"
    WAND = "wand"

class ArmorProficiency(str, Enum):
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"
    SHIELD = "shield"

class WeaponProficiency(str, Enum):
    CLUB           = "club"           
    DAGGER         = "dagger"         
    GREATCLUB      = "greatclub"      
    HANDAXE        = "handaxe"        
    JAVELIN        = "javelin"        
    LIGHT_HAMMER   = "light_hammer"   
    MACE           = "mace"           
    QUARTERSTAFF   = "quarterstaff"   
    SICKLE         = "sickle"         
    SPEAR          = "spear"          
    LIGHT_CROSSBOW = "crossbow_light" 
    DART           = "dart"           
    SHORTBOW       = "shortbow"       
    SLING          = "sling"          
    BATTLEAXE      = "battleaxe"      
    FLAIL          = "flail"          
    GLAIVE         = "glaive"         
    GREATAXE       = "greataxe"       
    GREATSWORD     = "greatsword"     
    HALBERD        = "halberd"        
    LANCE          = "lance"          
    LONGSWORD      = "longsword"      
    MAUL           = "maul"           
    MORNINGSTAR    = "morningstar"    
    PIKE           = "pike"           
    RAPIER         = "rapier"         
    SCIMITAR       = "scimitar"       
    SHORTSWORD     = "shortsword"     
    TRIDENT        = "trident"        
    WAR_PICK       = "war_pick"       
    WARHAMMER      = "warhammer"      
    WHIP           = "whip"           
    BLOWGUN        = "blowgun"        
    HAND_CROSSBOW  = "crossbow_hand"  
    HEAVY_CROSSBOW = "crossbow_heavy" 
    LONGBOW        = "longbow"        
    NET            = "net"                   

class ArtisanProficiency(str, Enum):
    ALCHEMISTS_SUPPLIES   = "alchemists_supplies"
    BREWERS_SUPPLIES      = "brewers_supplies"
    CALLIGRAPHERS_SUPPLIES = "calligraphers_supplies"
    CARPENTERS_TOOLS      = "carpenters_tools"
    CARTOGRAPHERS_TOOLS   = "cartographers_tools"
    SMITHS_TOOLS          = "smiths_tools"

class OtherToolProficiency(str, Enum):
    THIEVES_TOOLS         = "thieves_tools"
    HERBALISM_KIT         = "herbalism_kit"
    POISONERS_KIT         = "poisoners_kit"
    DISGUISE_KIT          = "disguise_kit"
    FORGERY_KIT           = "forgery_kit"
    NAVIGATORS_TOOLS      = "navigators_tools"

class InstrumentProficiency(str, Enum):
    LUTE   = "lute"
    DRUM   = "drum"
    FLUTE  = "flute"

class GamingProficiency(str, Enum):
    DICE_SET         = "dice_set"
    PLAYING_CARD_SET = "playing_card_set"

class VehicleProficiency(str, Enum):
    VEHICLE_LAND  = "vehicle_land"
    VEHICLE_WATER = "vehicle_water"

class FeatureTag(str, Enum):
    # Core
    RESOURCE                        = "resource"
    STAT_BONUS                      = "stat_bonus"
    SKILL                           = "skill"
    LANGUAGE                        = "language"
    COMBAT                          = "combat"
    HEALING                         = "healing"
    DEFENSIVE                       = "defensive"
    MOVEMENT                        = "movement"
    EXPLORATION                     = "exploration"
    REACTION                        = "reaction"
    IMMUNITY                        = "immunity"
    # Subclass
    SUBCLASS_CHOICE                 = "subclass_choice"
    SUBCLASS_FEATURE                = "subclass_feature"
    EPIC_BOON                       = "epic_boon"
    ASI                             = "asi"
    # Barbarian
    RAGE                            = "rage"
    RAGE_UPGRADE                    = "rage_upgrade"
    RAGE_UNLIMITED                  = "rage_unlimited"
    RECKLESS_ATTACK                 = "reckless_attack"
    DANGER_SENSE                    = "danger_sense"
    PRIMAL_KNOWLEDGE                = "primal_knowledge"
    EXTRA_ATTACK                    = "extra_attack"
    EXTRA_ATTACK_UPGRADE            = "extra_attack_upgrade"
    FAST_MOVEMENT                   = "fast_movement"
    FERAL_INSTINCT                  = "feral_instinct"
    BRUTAL_CRITICAL                 = "brutal_critical"
    BRUTAL_CRITICAL_UPGRADE         = "brutal_critical_upgrade"
    BRUTAL_STRIKE                   = "brutal_strike"
    BRUTAL_STRIKE_UPGRADE           = "brutal_strike_upgrade"
    RELENTLESS_RAGE                 = "relentless_rage"
    PERSISTENT_RAGE                 = "persistent_rage"
    INDOMITABLE_MIGHT               = "indomitable_might"
    INSTINCTIVE_POUNCE              = "instinctive_pounce"
    PRIMAL_CHAMPION                 = "primal_champion"
    PRIMAL_ORDER                    = "primal_order"
    # Bard
    BARDIC_INSPIRATION              = "bardic_inspiration"
    BARDIC_INSPIRATION_UPGRADE      = "bardic_inspiration_upgrade"
    JACK_OF_ALL_TRADES              = "jack_of_all_trades"
    SONG_OF_REST                    = "song_of_rest"
    SONG_OF_REST_UPGRADE            = "song_of_rest_upgrade"
    EXPERTISE                       = "expertise"
    EXPERTISE_UPGRADE               = "expertise_upgrade"
    FONT_OF_MAGIC                   = "font_of_magic"
    COUNTERCHARM                    = "countercharm"
    MAGICAL_SECRETS                 = "magical_secrets"
    MAGICAL_SECRETS_UPGRADE         = "magical_secrets_upgrade"
    MAGICAL_CUNNING                 = "magical_cunning"
    SUPERIOR_INSPIRATION            = "superior_inspiration"
    STROKE_OF_LUCK                  = "stroke_of_luck"
    # Cleric
    DIVINE_ORDER                    = "divine_order"
    CHANNEL_DIVINITY                = "channel_divinity"
    CHANNEL_DIVINITY_UPGRADE        = "channel_divinity_upgrade"
    DESTROY_UNDEAD                  = "destroy_undead"
    DESTROY_UNDEAD_UPGRADE          = "destroy_undead_upgrade"
    DIVINE_INTERVENTION             = "divine_intervention"
    DIVINE_INTERVENTION_UPGRADE     = "divine_intervention_upgrade"
    DIVINE_SENSE                    = "divine_sense"
    # Druid
    DRUIDIC                         = "druidic"
    WILD_SHAPE                      = "wild_shape"
    WILD_SHAPE_UPGRADE              = "wild_shape_upgrade"
    WILD_SHAPE_UNLIMITED            = "wild_shape_unlimited"
    TIMELESS_BODY                   = "timeless_body"
    BEAST_SPELLS                    = "beast_spells"
    ARCHDRUID                       = "archdruid"
    PRIMAL_AWARENESS                = "primal_awareness"
    PRIMEVAL_AWARENESS              = "primeval_awareness"
    LANDS_STRIDE                    = "lands_stride"
    NATURE_VEIL                     = "nature_veil"
    # Fighter
    FIGHTING_STYLE                  = "fighting_style"
    SECOND_WIND                     = "second_wind"
    ACTION_SURGE                    = "action_surge"
    ACTION_SURGE_UPGRADE            = "action_surge_upgrade"
    INDOMITABLE                     = "indomitable"
    INDOMITABLE_UPGRADE             = "indomitable_upgrade"
    WEAPON_MASTERY                  = "weapon_mastery"
    TACTICAL_MIND                   = "tactical_mind"
    TACTICAL_SHIFT                  = "tactical_shift"
    # Monk
    MARTIAL_ARTS                    = "martial_arts"
    MARTIAL_ARTS_UPGRADE            = "martial_arts_upgrade"
    KI                              = "ki"
    DISCIPLINE_POINTS               = "discipline_points"
    FLURRY_OF_BLOWS                 = "flurry_of_blows"
    PATIENT_DEFENSE                 = "patient_defense"
    STEP_OF_THE_WIND                = "step_of_the_wind"
    SLOW_FALL                       = "slow_fall"
    STUNNING_STRIKE                 = "stunning_strike"
    KI_EMPOWERED_STRIKES            = "ki_empowered_strikes"
    EVASION                         = "evasion"
    STILLNESS_OF_MIND               = "stillness_of_mind"
    PURITY_OF_BODY                  = "purity_of_body"
    TONGUE_OF_SUN_MOON              = "tongue_of_sun_moon"
    DIAMOND_SOUL                    = "diamond_soul"
    EMPTY_BODY                      = "empty_body"
    PERFECT_SELF                    = "perfect_self"
    DEFLECT_MISSILES                = "deflect_missiles"
    # Paladin
    LAY_ON_HANDS                    = "lay_on_hands"
    DIVINE_SMITE                    = "divine_smite"
    IMPROVED_DIVINE_SMITE           = "improved_divine_smite"
    DIVINE_HEALTH                   = "divine_health"
    AURA_OF_PROTECTION              = "aura_of_protection"
    AURA_OF_COURAGE                 = "aura_of_courage"
    AURA_UPGRADE                    = "aura_upgrade"
    CLEANSING_TOUCH                 = "cleansing_touch"
    TURN_UNDEAD                     = "turn_undead"
    ABJURE_FOES                     = "abjure_foes"
    FAITHFUL_STEED                  = "faithful_steed"
    RESTORING_TOUCH                 = "restoring_touch"
    RADIANT_STRIKES                 = "radiant_strikes"
    # Ranger
    FAVORED_ENEMY                   = "favored_enemy"
    FAVORED_ENEMY_UPGRADE           = "favored_enemy_upgrade"
    NATURAL_EXPLORER                = "natural_explorer"
    DEFT_EXPLORER                   = "deft_explorer"
    ROVING                          = "roving"
    TIRELESS                        = "tireless"
    FIGHTING_STYLE_RANGER           = "fighting_style_ranger"
    FERAL_SENSES                    = "feral_senses"
    FOE_SLAYER                      = "foe_slayer"
    HIDE_IN_PLAIN_SIGHT             = "hide_in_plain_sight"
    VANISH                          = "vanish"
    CONJURE_BARRAGE                 = "conjure_barrage"
    CONJURE_VOLLEY                  = "conjure_volley"
    PRECISE_HUNTER                  = "precise_hunter"
    # Rogue
    SNEAK_ATTACK                    = "sneak_attack"
    SNEAK_ATTACK_UPGRADE            = "sneak_attack_upgrade"
    THIEVES_CANT                    = "thieves_cant"
    CUNNING_ACTION                  = "cunning_action"
    CUNNING_STRIKE                  = "cunning_strike"
    DEVIOUS_STRIKES                 = "devious_strikes"
    UNCANNY_DODGE                   = "uncanny_dodge"
    RELIABLE_TALENT                 = "reliable_talent"
    BLINDSENSE                      = "blindsense"
    SLIPPERY_MIND                   = "slippery_mind"
    ELUSIVE                         = "elusive"
    STROKE_OF_LUCK_ROGUE            = "stroke_of_luck_rogue"
    STEADY_AIM                      = "steady_aim"
    SCHOLAR                         = "scholar"
    # Sorcerer
    INNATE_SORCERY                  = "innate_sorcery"
    METAMAGIC                       = "metamagic"
    METAMAGIC_UPGRADE               = "metamagic_upgrade"
    FLEXIBLE_CASTING                = "flexible_casting"
    SORCERY_INCARNATE               = "sorcery_incarnate"
    SPELL_MASTERY                   = "spell_mastery"
    SIGNATURE_SPELLS                = "signature_spells"
    CANTRIP_FORMULAS                = "cantrip_formulas"
    # Warlock
    PACT_MAGIC                      = "pact_magic"
    ELDRITCH_INVOCATIONS            = "eldritch_invocations"
    ELDRITCH_INVOCATIONS_UPGRADE    = "eldritch_invocations_upgrade"
    PACT_BOON                       = "pact_boon"
    MYSTIC_ARCANUM                  = "mystic_arcanum"
    MYSTIC_ARCANUM_UPGRADE          = "mystic_arcanum_upgrade"
    ELDRITCH_MASTER                 = "eldritch_master"
    CONTACT_PATRON                  = "contact_patron"
    # Wizard
    SPELLBOOK                       = "spellbook"
    ARCANE_RECOVERY                 = "arcane_recovery"
    SPELLCASTING                    = "spellcasting"
    # Bonuses / AC / Defense
    DAMAGE_BONUS                    = "damage_bonus"
    AC_BONUS                        = "ac_bonus"
    SPEED_BONUS                     = "speed_bonus"
    UNARMORED_DEFENSE               = "unarmored_defense"
    UNARMORED_MOVEMENT              = "unarmored_movement"
    UNARMORED_MOVEMENT_UPGRADE      = "unarmored_movement_upgrade"
    RESISTANCE_PHYSICAL             = "resistance_physical"
    # Advantage / Checks
    ADVANTAGE_INITIATIVE            = "advantage_initiative"
    ADVANTAGE_STR_CHECK             = "advantage_STR_check"
    # Special
    SURPRISED_IMMUNITY_WHILE_RAGING = "surprised_immunity_while_raging"
    TRANSFORMATION                  = "transformation"
    STEALTH                         = "stealth"

class FeatureType(str, Enum):
    PASSIVE      = "passive"
    ACTION       = "action"
    BONUS_ACTION = "bonus_action"
    REACTION     = "reaction"

class FeatTag(str, Enum):
    COMBAT          = "combat"
    MAGIC           = "magic"
    SKILL           = "skill"
    DEFENSE         = "defense"
    DAMAGE_BONUS    = "damage_bonus"
    UTILITY         = "utility"
    SPELLCASTING    = "spellcasting"
    TOOL_PROFICIENCY = "tool_proficiency"
    SUPPORT         = "support"
    ORIGIN          = "origin"
    CRAFTING        = "crafting"
    MUSIC           = "music"
    CLERIC          = "cleric"
    DRUID           = "druid"
    WIZARD          = "wizard"

class FeatType(str, Enum):
    PASSIVE      = "passive"
    ACTION       = "action"
    BONUS_ACTION = "bonus_action"
    REACTION     = "reaction"

class EffectType(str, Enum):
    STAT_BONUS         = "stat_bonus"
    STAT_SET           = "stat_set"
    RESISTANCE         = "resistance"
    IMMUNITY           = "immunity"
    ADVANTAGE          = "advantage"
    DISADVANTAGE       = "disadvantage"
    RESOURCE           = "resource"
    AC_FORMULA         = "ac_formula"
    SPEED_BONUS        = "speed_bonus"
    SPEED_GRANT        = "speed_grant"
    PROFICIENCY        = "proficiency"
    LIGHT_SOURCE       = "light_source"
    AREA_HAZARD        = "area_hazard"
    STABILIZE          = "stabilize"
    RESTORE_HP         = "restore_hp"
    DAMAGE_ON_TRIGGER  = "damage_on_trigger"
    CONDITION_APPLY    = "condition_apply"
    SPELL_EFFECT       = "spell_effect"
    NARRATIVE_FEATURE  = "narrative_feature"
    SPECIAL            = "special"      # dispatch via index; keine strukturierten Felder möglich

class Condition(str, Enum):
    BLINDED       = "blinded"
    CHARMED       = "charmed"
    DEAFENED      = "deafened"
    EXHAUSTION    = "exhaustion"
    FRIGHTENED    = "frightened"
    GRAPPLED      = "grappled"
    INCAPACITATED = "incapacitated"
    INVISIBLE     = "invisible"
    PARALYZED     = "paralyzed"
    PETRIFIED     = "petrified"
    POISONED      = "poisoned"
    PRONE         = "prone"
    RESTRAINED    = "restrained"
    STUNNED       = "stunned"
    SURPRISED     = "surprised"
    UNCONSCIOUS   = "unconscious"

class AoEType(str, Enum):
    SPHERE   = "sphere"
    CONE     = "cone"
    LINE     = "line"
    CYLINDER = "cylinder"
    CUBE     = "cube"

class SpellAttackType(str, Enum):
    RANGED_SPELL = "ranged_spell"
    MELEE_SPELL  = "melee_spell"

class EffectCondition(str, Enum):
    WHILE_RAGING        = "while_raging"
    NO_ARMOR            = "no_armor"
    NO_SHIELD           = "no_shield"
    NO_HEAVY_ARMOR      = "no_heavy_armor"
    ON_HIT              = "on_hit"
    ON_CRITICAL_HIT     = "on_critical_hit"
    WHILE_CONCENTRATING = "while_concentrating"
    ON_ENTER            = "on_enter"
    IN_SUNLIGHT         = "in_sunlight"

class EffectRecipient(str, Enum):
    SELF             = "self"
    TARGET           = "target"
    ALLY             = "ally"
    ENEMY            = "enemy"
    MULTIPLE_TARGETS = "multiple_targets"
    AREA_OF_EFFECT   = "area_of_effect"
    OWNER            = "owner"

class DieType(str, Enum):
    D1  = "d1"
    D4  = "d4"
    D6  = "d6"
    D8  = "d8"
    D10 = "d10"
    D12 = "d12"
    D20 = "d20"

class DamageType(str, Enum):
    BLUDGEONING    = "bludgeoning"
    PIERCING       = "piercing"
    SLASHING       = "slashing"
    FIRE           = "fire"
    COLD           = "cold"
    LIGHTNING      = "lightning"
    THUNDER        = "thunder"
    ACID           = "acid"
    POISON         = "poison"
    NECROTIC       = "necrotic"
    RADIANT        = "radiant"
    PSYCHIC        = "psychic"
    FORCE          = "force"

class Size(str, Enum):
    TINY       = "tiny"
    SMALL      = "small"
    MEDIUM     = "medium"
    LARGE      = "large"
    HUGE       = "huge"
    GARGANTUAN = "gargantuan"


class SpellCastingType(str, Enum):
    KNOWN     = "known"
    PREPARED  = "prepared"
    SPELLBOOK = "spellbook"
    PACT      = "pact"

class SpellSchool(str, Enum):
    ABJURATION    = "abjuration"
    CONJURATION   = "conjuration"
    DIVINATION    = "divination"
    ENCHANTMENT   = "enchantment"
    EVOCATION     = "evocation"
    ILLUSION      = "illusion"
    NECROMANCY    = "necromancy"
    TRANSMUTATION = "transmutation"

class EnvironmentStat(str, Enum):
    LIGHT_RADIUS_BRIGHT = "light_radius_bright"
    LIGHT_RADIUS_DIM    = "light_radius_dim"

class ChoiceType(str, Enum):
    DAMAGE_TYPE  = "damage_type"
    TOOL         = "tool"
    WEAPON       = "weapon"
    SKILL        = "skill"
    LANGUAGE     = "language"
    SPELL_CLASS  = "spell_class"

class EffectSourceCategory(str, Enum):
    CLASS_FEATURE = "class_feature"
    FEAT          = "feat"
    ITEM          = "item"
    SPELL         = "spell"
    BACKGROUND    = "background"

class RefreshOn(str, Enum):
    SHORT_REST = "short_rest"
    LONG_REST  = "long_rest"
    DAWN       = "dawn"
    NEVER      = "never"

# alias
Stat: TypeAlias = Ability | HpStat | CombatStat | AbilityCheck | AbilitySavingThrow | Skill | ResourceStat
ItemCategory: TypeAlias = WeaponCategory | ArmorCategory | EquipmentCategory | MagicItemCategory
WeaponProficiencyAll: TypeAlias = WeaponCategory | WeaponProficiency
ArmorProficiencyAll: TypeAlias = ArmorProficiency # für später falls ich dies auch um einzel rüstungen erweitern möchte für custom content und regelwerke
ToolProficiency: TypeAlias = ArtisanProficiency | OtherToolProficiency | InstrumentProficiency | GamingProficiency | VehicleProficiency
EffectTarget: TypeAlias = Stat | DamageType | AbilityCheck | AbilitySavingThrow | AttackType | EnvironmentStat