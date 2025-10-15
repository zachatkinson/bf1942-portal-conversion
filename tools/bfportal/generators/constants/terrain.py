#!/usr/bin/env python3
"""Terrain and coordinate system constants.

Single Responsibility: Define terrain-specific calibration values and defaults.

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-13
"""

# ==============================================================================
# Default Values
# ==============================================================================

# Default combat area if no bounds provided
DEFAULT_MAP_SIZE_M = 2048.0  # 2048x2048m default map
DEFAULT_CENTER_HEIGHT_M = 0.0  # Default Y position for combat area center (ground level)

# ==============================================================================
# Terrain-Specific Calibration
# ==============================================================================

# MP_Tungsten mesh calibration
MP_TUNGSTEN_MESH_CENTER_X = 59.0
MP_TUNGSTEN_MESH_CENTER_Z = -295.0

# Post-rotation translation for 90° CW rotated MP_Tungsten
# After rotation, mesh center moves from (59, -295) to (295, -59)
# To center at origin, translate by (295, 59)
MP_TUNGSTEN_ROTATED_OFFSET_X = 295.0
MP_TUNGSTEN_ROTATED_OFFSET_Z = 59.0

# ==============================================================================
# BF1942 Terrain Defaults
# ==============================================================================

# Default height scale for BF1942 heightmaps
BF1942_DEFAULT_HEIGHT_SCALE = 150.0  # Typical scale for BF1942 16-bit heightmaps

# Default terrain size for BF1942 maps
BF1942_DEFAULT_TERRAIN_SIZE = 1024.0  # meters (typical map size)

# Terrain height adjustment tolerance for map rebasing
TERRAIN_HEIGHT_ADJUSTMENT_TOLERANCE_M = 2.0  # Objects within 2m of terrain are not adjusted
