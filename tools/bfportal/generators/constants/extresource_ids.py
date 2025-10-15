#!/usr/bin/env python3
"""ExtResource ID constants for Godot .tscn generation.

Single Responsibility: Define ExtResource IDs for Portal SDK scenes.

These IDs MUST match the order in TscnGenerator._init_ext_resources().
If you add/remove/reorder ExtResources, update these constants!

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-13
"""

# ==============================================================================
# ExtResource IDs - Portal SDK Scene References
# ==============================================================================

EXT_RESOURCE_HQ_SPAWNER = "1"  # HQ_PlayerSpawner.tscn
EXT_RESOURCE_SPAWN_POINT = "2"  # SpawnPoint.tscn
EXT_RESOURCE_CAPTURE_POINT = "3"  # CapturePoint.tscn
EXT_RESOURCE_VEHICLE_SPAWNER = "4"  # VehicleSpawner.tscn
EXT_RESOURCE_STATIONARY_EMPLACEMENT = "5"  # StationaryEmplacementSpawner.tscn
EXT_RESOURCE_COMBAT_AREA = "6"  # CombatArea.tscn
EXT_RESOURCE_DEPLOY_CAM = "7"  # DeployCam.tscn (REQUIRED for spawn screen to work)
EXT_RESOURCE_TERRAIN = "8"  # {base_terrain}_Terrain.tscn (dynamic)
EXT_RESOURCE_ASSETS = "9"  # {base_terrain}_Assets.tscn (dynamic, hidden to suppress auto-load)
EXT_RESOURCE_POLYGON_VOLUME = "10"  # PolygonVolume.tscn
EXT_RESOURCE_WORLD_ICON = "11"  # WorldIcon.tscn (for capture point labels A, B, C)

# Starting ID for dynamically registered static assets
EXT_RESOURCE_STATIC_ASSETS_START = 12
