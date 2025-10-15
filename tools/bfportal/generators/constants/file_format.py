#!/usr/bin/env python3
"""Godot .tscn file format constants.

Single Responsibility: Define .tscn file format values and asset filtering rules.

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-13
"""

# ==============================================================================
# File Format Constants
# ==============================================================================

TSCN_FORMAT_VERSION = 3  # Godot 4 .tscn format version
TSCN_SCENE_TYPE = "gd_scene"

# ==============================================================================
# Asset Filtering (for categorizing game objects)
# ==============================================================================

# Keywords to exclude from static layer (already handled by specialized generators)
GAMEPLAY_KEYWORDS = [
    "vehicle",
    "spawner",
    "spawnpoint",
    "spawn",
    "controlpoint",
    "capturepoint",
    "cpoint",
]

# ==============================================================================
# Debug and Logging
# ==============================================================================

# Maximum number of assets to log detailed debug info for (prevent spam)
DEBUG_ASSET_LOG_LIMIT = 5
