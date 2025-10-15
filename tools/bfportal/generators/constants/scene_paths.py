#!/usr/bin/env python3
"""Portal SDK scene path constants.

Single Responsibility: Define res:// paths to Portal SDK .tscn scene files.

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-13
"""

# ==============================================================================
# Portal SDK Scene Paths
# ==============================================================================

SCENE_PATH_HQ_SPAWNER = "res://objects/Gameplay/Common/HQ_PlayerSpawner.tscn"
SCENE_PATH_SPAWN_POINT = "res://objects/entities/SpawnPoint.tscn"
SCENE_PATH_CAPTURE_POINT = "res://objects/Gameplay/Conquest/CapturePoint.tscn"
SCENE_PATH_VEHICLE_SPAWNER = "res://objects/Gameplay/Common/VehicleSpawner.tscn"
SCENE_PATH_STATIONARY_EMPLACEMENT = (
    "res://objects/Gameplay/Common/StationaryEmplacementSpawner.tscn"
)
SCENE_PATH_COMBAT_AREA = "res://objects/Gameplay/Common/CombatArea.tscn"
SCENE_PATH_DEPLOY_CAM = "res://objects/Gameplay/Common/DeployCam.tscn"
SCENE_PATH_WORLD_ICON = "res://objects/Gameplay/Common/WorldIcon.tscn"
SCENE_PATH_POLYGON_VOLUME = (
    "res://addons/bf_portal/portal_tools/types/PolygonVolume/PolygonVolume.tscn"
)

# Dynamic terrain paths (format with base_terrain name)
SCENE_PATH_TERRAIN_FORMAT = "res://static/{base_terrain}_Terrain.tscn"
SCENE_PATH_ASSETS_FORMAT = "res://static/{base_terrain}_Assets.tscn"
