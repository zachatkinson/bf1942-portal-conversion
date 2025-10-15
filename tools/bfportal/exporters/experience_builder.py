#!/usr/bin/env python3
"""
Portal experience file builder utilities.

This module provides shared utilities for creating Portal experience files
with proper structure to ensure map rotation appears pre-populated in the
Portal web builder UI.
"""

import uuid
from typing import Any

from ..generators.constants.experience import (
    AI_MAX_COUNT_PER_TEAM_DEFAULT,
    EXPERIENCE_GAMEMODE_CUSTOM,
    EXPERIENCE_PATCHID_DEFAULT,
    MAX_PLAYERS_PER_TEAM_DEFAULT,
    MODBUILDER_GAMEMODE_VERIFIED,
    create_default_mutators,
    create_team_composition,
)


def create_spatial_attachment(
    map_id: str,
    map_name: str,
    spatial_base64: str,
    map_index: int = 0,
) -> dict[str, Any]:
    """
    Create a spatial attachment structure for Portal experiences.

    Portal requires spatial attachments to exist in TWO locations:
    1. Nested inside mapRotation entries (mapRotation[].spatialAttachment)
    2. In the root-level attachments array (attachments[])

    Both must reference the same UUID for Portal to recognize the attachment.

    Args:
        map_id: Unique identifier for the map (e.g., "kursk")
        map_name: Display name for the map (e.g., "Kursk")
        spatial_base64: Base64-encoded spatial.json data
        map_index: Index of map in rotation (default: 0)

    Returns:
        Spatial attachment dictionary ready for use in both locations

    Example:
        >>> spatial_base64 = base64.b64encode(spatial_json.encode()).decode()
        >>> attachment = create_spatial_attachment(
        ...     map_id="kursk",
        ...     map_name="Kursk",
        ...     spatial_base64=spatial_base64,
        ...     map_index=0
        ... )
        >>> experience = {
        ...     "gameMode": "ModBuilderCustom",
        ...     "mutators": {"ModBuilder_GameMode": 2, ...},
        ...     "mapRotation": [{
        ...         "id": "MP_Tungsten-ModBuilderCustom0",
        ...         "spatialAttachment": attachment
        ...     }],
        ...     "attachments": [attachment]  # Same object in both places
        ... }
    """
    # Generate UUID for this spatial attachment (matches Portal's format)
    attachment_id = str(uuid.uuid4())

    return {
        "id": attachment_id,
        "filename": f"{map_name}.spatial.json",
        "metadata": f"mapIdx={map_index}",
        "version": "123",  # Portal SDK version format
        "isProcessable": True,
        "processingStatus": 2,  # 2 = processed/ready
        "attachmentData": {
            "original": spatial_base64,
            "compiled": "",  # Empty - Portal compiles server-side
        },
        "attachmentType": 1,  # 1 = spatial attachment
        "errors": [],
    }


def create_portal_experience(
    name: str,
    description: str,
    map_rotation: list[dict[str, Any]],
    attachments: list[dict[str, Any]],
    max_players_per_team: int = MAX_PLAYERS_PER_TEAM_DEFAULT,
    game_mode: str = EXPERIENCE_GAMEMODE_CUSTOM,
    modbuilder_gamemode: int = MODBUILDER_GAMEMODE_VERIFIED,
) -> dict[str, Any]:
    """
    Create a complete Portal experience structure (DRY - shared by all experience creators).

    This is the single source of truth for Portal experience file format.
    Used by both single-map and multi-map experience creators.

    Args:
        name: Experience name (e.g., "Kursk - BF1942 Classic")
        description: Experience description
        map_rotation: List of map entries with spatialAttachment
        attachments: Root-level attachments array (must match map_rotation spatialAttachments)
        max_players_per_team: Players per team (16, 32, or 64)
        game_mode: Game mode string (default: "ModBuilderCustom")
        modbuilder_gamemode: ModBuilder mode (0=Custom, 2=Verified)

    Returns:
        Complete Portal experience dictionary ready for JSON export

    Example:
        >>> spatial = create_spatial_attachment("kursk", "Kursk", spatial_base64, 0)
        >>> experience = create_portal_experience(
        ...     name="Kursk - BF1942 Classic",
        ...     description="Classic Eastern Front battle",
        ...     map_rotation=[{"id": "MP_Tungsten-ModBuilderCustom0", "spatialAttachment": spatial}],
        ...     attachments=[spatial],
        ...     max_players_per_team=32
        ... )
    """
    return {
        "mutators": create_default_mutators(
            max_players_per_team=max_players_per_team,
            ai_max_count_per_team=AI_MAX_COUNT_PER_TEAM_DEFAULT,
            modbuilder_gamemode=modbuilder_gamemode,
        ),
        "assetRestrictions": {},
        "gameMode": game_mode,
        "name": name,
        "description": description,
        "mapRotation": map_rotation,
        "patchId": EXPERIENCE_PATCHID_DEFAULT,
        "workspace": {},
        "teamComposition": create_team_composition(
            max_players_per_team=max_players_per_team,
            ai_capacity_per_team=AI_MAX_COUNT_PER_TEAM_DEFAULT,
        ),
        # CRITICAL: Portal requires spatial attachment in BOTH mapRotation AND root attachments
        # Both must reference the same UUID for Portal to recognize the attachment
        "attachments": attachments,
    }
