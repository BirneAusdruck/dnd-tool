# Public API for src.shared — import everything you need from here.

# Domain Definitions
from src.shared.domain.definitions import (
    ClassDefinition,
    SpellcastingInfo,
    SkillChoices,
    SpellDefinition,
    FeatDefinition,
    ItemDefinition,
)

# Runtime Objects
from src.shared.runtime import (
    Character,
    CharacterClass,
    ActiveEffect,
    CombatEncounter,
    CombatantEntry,
)

# Services
from src.shared.services import (
    ClassService,
    SpellService,
    FeatService,
    ItemService,
    RaceService,
    BackgroundService,
    LevelUpService,
    CharacterBuilderService,
    SRDConstants,
)

# Systems
from src.shared.systems import (
    DiceSystem,
    LevelUpSystem,
    CombatSystem,
    EffectResolutionSystem,
)

# Edition management
from src.shared.repositories.srd_repository import (
    set_edition,
    get_active_edition,
)

__all__ = [
    # Definitions
    "ClassDefinition",
    "SpellcastingInfo",
    "SkillChoices",
    "SpellDefinition",
    "FeatDefinition",
    "ItemDefinition",
    # Runtime
    "Character",
    "CharacterClass",
    "ActiveEffect",
    "CombatEncounter",
    "CombatantEntry",
    # Services
    "ClassService",
    "SpellService",
    "FeatService",
    "ItemService",
    "RaceService",
    "BackgroundService",
    "LevelUpService",
    "CharacterBuilderService",
    "SRDConstants",
    # Systems
    "DiceSystem",
    "LevelUpSystem",
    "CombatSystem",
    "EffectResolutionSystem",
    # Edition
    "set_edition",
    "get_active_edition",
]
