#!/usr/bin/env python3
"""Constants package for BF Portal TSCN generation - DRY/SOLID architecture.

This package provides a modular constants system following SOLID principles:
- Single Responsibility: Each module focuses on one domain (ExtResource IDs, gameplay, terrain, etc.)
- Open/Closed: Easy to extend with new constant modules without modifying existing ones
- DRY: Single source of truth for all magic numbers and strings

Usage:
    # Import everything (convenience for main generators)
    from .constants import *

    # Or import specific modules (better for focused use)
    from .constants.extresource_ids import EXT_RESOURCE_HQ_SPAWNER
    from .constants.gameplay import HQ_PROTECTION_RADIUS_M

Module Structure:
    extresource_ids.py  - Godot ExtResource ID constants
    scene_paths.py      - Portal SDK scene paths
    gameplay.py         - Gameplay values (HQ zones, capture areas, spawn requirements)
    terrain.py          - Terrain calibration and coordinate system values
    file_format.py      - .tscn file format and asset filtering
    validation.py       - Validation error messages

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-13
"""

# Re-export all constants for convenience
# ruff: noqa: F405
from .clearance import *  # noqa: F403
from .experience import *  # noqa: F403
from .extresource_ids import *  # noqa: F403
from .file_format import *  # noqa: F403
from .gameplay import *  # noqa: F403
from .paths import *  # noqa: F403
from .scene_paths import *  # noqa: F403
from .terrain import *  # noqa: F403
from .validation import *  # noqa: F403

__all__ = [  # noqa: F405
    # Clearance constants
    "GROUND_CLEARANCE_M",
    "SPAWN_CLEARANCE_M",
    "VEHICLE_SPAWN_CLEARANCE_M",
    "CAPTURE_POINT_CLEARANCE_M",
    "INITIAL_PLACEMENT_SAFETY_CLEARANCE_M",
    "DEPLOY_CAM_VIEWING_DISTANCE_MULTIPLIER",
    "DEPLOY_CAM_SAFETY_CLEARANCE_M",
    "DEPLOY_CAM_DEFAULT_HEIGHT_M",
    "MANUAL_OFFSET_X_DEFAULT",
    "MANUAL_OFFSET_Z_DEFAULT",
    # Experience constants
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
    # ExtResource IDs
    "EXT_RESOURCE_HQ_SPAWNER",
    "EXT_RESOURCE_SPAWN_POINT",
    "EXT_RESOURCE_CAPTURE_POINT",
    "EXT_RESOURCE_VEHICLE_SPAWNER",
    "EXT_RESOURCE_STATIONARY_EMPLACEMENT",
    "EXT_RESOURCE_COMBAT_AREA",
    "EXT_RESOURCE_DEPLOY_CAM",
    "EXT_RESOURCE_TERRAIN",
    "EXT_RESOURCE_ASSETS",
    "EXT_RESOURCE_POLYGON_VOLUME",
    "EXT_RESOURCE_WORLD_ICON",
    "EXT_RESOURCE_STATIC_ASSETS_START",
    # Scene paths
    "SCENE_PATH_HQ_SPAWNER",
    "SCENE_PATH_SPAWN_POINT",
    "SCENE_PATH_CAPTURE_POINT",
    "SCENE_PATH_VEHICLE_SPAWNER",
    "SCENE_PATH_STATIONARY_EMPLACEMENT",
    "SCENE_PATH_COMBAT_AREA",
    "SCENE_PATH_DEPLOY_CAM",
    "SCENE_PATH_POLYGON_VOLUME",
    "SCENE_PATH_WORLD_ICON",
    "SCENE_PATH_TERRAIN_FORMAT",
    "SCENE_PATH_ASSETS_FORMAT",
    # Gameplay constants
    "HQ_PROTECTION_RADIUS_M",
    "HQ_PROTECTION_HEIGHT_M",
    "COMBAT_AREA_HEIGHT_M",
    "COMBAT_AREA_EXCLUSION_ZONE_M",
    "CAPTURE_ZONE_HEIGHT_M",
    "OBJID_HQ_START",
    "OBJID_WORLD_ICON_START",
    "OBJID_CAPTURE_POINTS_START",
    "OBJID_VEHICLE_SPAWNERS_START",
    "OBJID_STATIONARY_EMPLACEMENTS_START",
    "MIN_SPAWNS_PER_TEAM",
    # Terrain constants
    "DEFAULT_MAP_SIZE_M",
    "DEFAULT_CENTER_HEIGHT_M",
    "MP_TUNGSTEN_MESH_CENTER_X",
    "MP_TUNGSTEN_MESH_CENTER_Z",
    "MP_TUNGSTEN_ROTATED_OFFSET_X",
    "MP_TUNGSTEN_ROTATED_OFFSET_Z",
    # File format
    "TSCN_FORMAT_VERSION",
    "TSCN_SCENE_TYPE",
    "GAMEPLAY_KEYWORDS",
    "DEBUG_ASSET_LOG_LIMIT",
    # Validation messages
    "ERROR_MISSING_TEAM1_HQ",
    "ERROR_MISSING_TEAM2_HQ",
    "ERROR_INSUFFICIENT_TEAM1_SPAWNS",
    "ERROR_INSUFFICIENT_TEAM2_SPAWNS",
    "ERROR_FILE_NOT_FOUND",
    # Path constants and helpers
    "get_project_root",
    "get_godot_project_dir",
    "get_fb_export_data_dir",
    "get_spatial_levels_dir",
    "get_asset_types_path",
    "get_level_tscn_path",
    "get_spatial_json_path",
    "get_bf1942_level_path",
    "get_terrain_glb_path",
    "DIR_BF1942_SOURCE",
    "DIR_BF1942_EXTRACTED",
    "DIR_GODOT_PROJECT",
    "DIR_GODOT_LEVELS",
    "DIR_GODOT_OBJECTS",
    "DIR_GODOT_STATIC",
    "DIR_GODOT_RAW_MODELS",
    "DIR_FB_EXPORT_DATA",
    "DIR_FB_EXPORT_LEVELS",
    "DIR_TOOLS",
    "DIR_TOOLS_BFPORTAL",
    "DIR_MODS",
    "FILE_ASSET_TYPES",
    "FILE_LEVEL_INFO",
    "FILE_PROJECT_GODOT",
    "FILE_README",
    "FILE_README_HTML",
    "DIR_BF1942_RFA_BASE",
    "DIR_BF1942_RFA_XPACK1",
    "DIR_BF1942_RFA_XPACK2",
    "DIR_BF1942_EXTRACTED_BASE",
    "DIR_BF1942_EXTRACTED_XPACK1",
    "DIR_BF1942_EXTRACTED_XPACK2",
]
