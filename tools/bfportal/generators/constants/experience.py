#!/usr/bin/env python3
"""Portal experience creation constants.

Single Responsibility: Define Portal experience structure defaults and settings.

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-13
"""

# ==============================================================================
# Portal Experience Mutator Defaults
# ==============================================================================

# Game mode configuration
# IMPORTANT: Labels were backwards! Portal UI confirms:
# - Verified mode (0) = NO custom spatials allowed
# - Custom mode (2) = Custom spatials allowed (but unverified)
MODBUILDER_GAMEMODE_VERIFIED = 0  # Verified mode (NO spatials, earns XP)
MODBUILDER_GAMEMODE_CUSTOM = 2  # Custom mode (allows spatials, unverified)

# AI settings
AI_SPAWN_TYPE_DEFAULT = 2
AI_MANDOWN_EXPERIENCE_TYPE_DEFAULT = 1  # AI respawn behavior

# Gameplay settings
AIM_ASSIST_SNAP_RADIUS_MULTIPLIER_DEFAULT = 1
FRIENDLY_FIRE_REFLECTION_MAX_TEAMKILLS_DEFAULT = 2
SPAWN_BALANCING_GAMEMODE_START_TIMER_DEFAULT = 0
SPAWN_BALANCING_GAMEMODE_PLAYER_COUNT_RATIO_DEFAULT = 0.75

# ==============================================================================
# Player Count Defaults
# ==============================================================================

MAX_PLAYERS_PER_TEAM_DEFAULT = 32  # 32v32 = 64 players total
AI_MAX_COUNT_PER_TEAM_DEFAULT = 0  # No AI by default

# ==============================================================================
# Portal Experience Structure
# ==============================================================================

# CRITICAL: gameMode field behavior in Portal experiences
# - "ModBuilderCustom" = Required when using custom spatial data (custom maps)
# - Can be used with EITHER ModBuilder_GameMode 0 (Custom) OR 2 (Verified)
# - Verified mode (2) with "ModBuilderCustom" = Full XP progression + custom maps!
# - The actual game mode (Conquest/Rush/etc) is determined by map's gameplay nodes
EXPERIENCE_GAMEMODE_CUSTOM = "ModBuilderCustom"  # Required for custom spatial data
EXPERIENCE_PATCHID_DEFAULT = None  # Portal includes this field

# ==============================================================================
# Team Composition Defaults
# ==============================================================================

TEAM_AI_TYPE_DEFAULT = 0  # No AI


def create_default_mutators(
    max_players_per_team: int = MAX_PLAYERS_PER_TEAM_DEFAULT,
    ai_max_count_per_team: int = AI_MAX_COUNT_PER_TEAM_DEFAULT,
    modbuilder_gamemode: int = MODBUILDER_GAMEMODE_VERIFIED,
) -> dict:
    """Create default Portal experience mutators.

    Args:
        max_players_per_team: Maximum human players per team
        ai_max_count_per_team: Maximum AI bots per team
        modbuilder_gamemode: Game mode type (0=Custom, 2=Verified)

    Returns:
        Mutators dictionary following Portal format
    """
    return {
        "MaxPlayerCount_PerTeam": max_players_per_team,
        "AiMaxCount_PerTeam": ai_max_count_per_team,
        "AiSpawnType": AI_SPAWN_TYPE_DEFAULT,
        "AI_ManDownExperienceType_PerTeam": AI_MANDOWN_EXPERIENCE_TYPE_DEFAULT,
        "ModBuilder_GameMode": modbuilder_gamemode,
        "AimAssistSnapCapsuleRadiusMultiplier": AIM_ASSIST_SNAP_RADIUS_MULTIPLIER_DEFAULT,
        "FriendlyFireDamageReflectionMaxTeamKills": FRIENDLY_FIRE_REFLECTION_MAX_TEAMKILLS_DEFAULT,
        "SpawnBalancing_GamemodeStartTimer": SPAWN_BALANCING_GAMEMODE_START_TIMER_DEFAULT,
        "SpawnBalancing_GamemodePlayerCountRatio": SPAWN_BALANCING_GAMEMODE_PLAYER_COUNT_RATIO_DEFAULT,
    }


def create_team_composition(
    max_players_per_team: int = MAX_PLAYERS_PER_TEAM_DEFAULT,
    ai_capacity_per_team: int = AI_MAX_COUNT_PER_TEAM_DEFAULT,
) -> list:
    """Create team composition for Portal experience.

    Args:
        max_players_per_team: Human capacity per team
        ai_capacity_per_team: AI capacity per team

    Returns:
        Team composition list following Portal format
    """
    return [
        [
            1,
            {
                "humanCapacity": max_players_per_team,
                "aiCapacity": ai_capacity_per_team,
                "aiType": TEAM_AI_TYPE_DEFAULT,
            },
        ],
        [
            2,
            {
                "humanCapacity": max_players_per_team,
                "aiCapacity": ai_capacity_per_team,
                "aiType": TEAM_AI_TYPE_DEFAULT,
            },
        ],
    ]


__all__ = [
    "MODBUILDER_GAMEMODE_CUSTOM",
    "MODBUILDER_GAMEMODE_VERIFIED",
    "AI_SPAWN_TYPE_DEFAULT",
    "AI_MANDOWN_EXPERIENCE_TYPE_DEFAULT",
    "AIM_ASSIST_SNAP_RADIUS_MULTIPLIER_DEFAULT",
    "FRIENDLY_FIRE_REFLECTION_MAX_TEAMKILLS_DEFAULT",
    "SPAWN_BALANCING_GAMEMODE_START_TIMER_DEFAULT",
    "SPAWN_BALANCING_GAMEMODE_PLAYER_COUNT_RATIO_DEFAULT",
    "MAX_PLAYERS_PER_TEAM_DEFAULT",
    "AI_MAX_COUNT_PER_TEAM_DEFAULT",
    "EXPERIENCE_GAMEMODE_CUSTOM",
    "EXPERIENCE_PATCHID_DEFAULT",
    "TEAM_AI_TYPE_DEFAULT",
    "create_default_mutators",
    "create_team_composition",
]
