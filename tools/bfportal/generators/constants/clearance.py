#!/usr/bin/env python3
"""Ground clearance and offset constants.

Single Responsibility: Define height offsets for object placement.

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-13
"""

# ==============================================================================
# Ground Clearance Heights (meters above terrain)
# ==============================================================================

# Standard ground clearance for objects placed on terrain
GROUND_CLEARANCE_M = 0.0  # Flush with terrain surface

# Spawn point clearance (prevents players spawning inside terrain)
SPAWN_CLEARANCE_M = 1.0  # 1 meter above terrain

# Vehicle spawn clearance
VEHICLE_SPAWN_CLEARANCE_M = 0.5  # Slightly above ground for physics

# Capture point clearance
CAPTURE_POINT_CLEARANCE_M = 0.0  # Flush with ground (trigger area)

# ==============================================================================
# Initial Placement Safety (Before Terrain Snapping)
# ==============================================================================

# Safety clearance for initial object placement above highest terrain point
# Ensures objects start ABOVE terrain so terrain snapping can raycast downward
# Without this, objects placed underground cannot snap to terrain (no collision below them)
INITIAL_PLACEMENT_SAFETY_CLEARANCE_M = 50.0  # Start 50m above max terrain height

# ==============================================================================
# DeployCam (Spawn Screen Camera) Constants
# ==============================================================================

# Viewing distance multiplier for deploy camera height calculation
# Camera height = terrain_max_y + (max_dimension * multiplier) + clearance
DEPLOY_CAM_VIEWING_DISTANCE_MULTIPLIER = 0.75  # 75% of map dimension for good angle

# Safety clearance above calculated viewing distance
DEPLOY_CAM_SAFETY_CLEARANCE_M = 100.0  # Extra 100m above viewing distance

# Default deploy camera height when bounds unknown
DEPLOY_CAM_DEFAULT_HEIGHT_M = 600.0  # Fallback height for unbounded maps

# ==============================================================================
# Manual Offset Defaults (for rotated terrain recentering)
# ==============================================================================

MANUAL_OFFSET_X_DEFAULT = 0.0  # Target X position for asset centroid
MANUAL_OFFSET_Z_DEFAULT = 0.0  # Target Z position for asset centroid

__all__ = [
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
]
