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
# Manual Offset Defaults (for rotated terrain recentering)
# ==============================================================================

MANUAL_OFFSET_X_DEFAULT = 0.0  # Target X position for asset centroid
MANUAL_OFFSET_Z_DEFAULT = 0.0  # Target Z position for asset centroid

__all__ = [
    "GROUND_CLEARANCE_M",
    "SPAWN_CLEARANCE_M",
    "VEHICLE_SPAWN_CLEARANCE_M",
    "CAPTURE_POINT_CLEARANCE_M",
    "MANUAL_OFFSET_X_DEFAULT",
    "MANUAL_OFFSET_Z_DEFAULT",
]
