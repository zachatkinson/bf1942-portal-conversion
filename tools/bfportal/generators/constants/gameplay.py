#!/usr/bin/env python3
"""Gameplay constants for Portal map generation.

Single Responsibility: Define gameplay-related values (HQ zones, capture areas, spawn requirements, etc.)

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-13
"""

# ==============================================================================
# HQ Protection Zone
# ==============================================================================

HQ_PROTECTION_RADIUS_M = 50.0  # 50m square around HQ (BF1942 standard)
HQ_PROTECTION_HEIGHT_M = 50.0  # Height of HQ safety zone

# ==============================================================================
# Combat Area
# ==============================================================================

COMBAT_AREA_HEIGHT_M = 500.0  # Vertical extent of combat zone (Portal SDK standard)
COMBAT_AREA_EXCLUSION_ZONE_M = 20.0  # Inset from terrain edges

# ==============================================================================
# Capture Points
# ==============================================================================

CAPTURE_ZONE_HEIGHT_M = 50.0  # Height of capture zone trigger

# ==============================================================================
# Object ID Ranges (for Portal scripting)
# ==============================================================================

OBJID_HQ_START = 1  # Team HQs: 1, 2
OBJID_WORLD_ICON_START = 20  # WorldIcon labels (CP labels): 20, 21, 22...
OBJID_CAPTURE_POINTS_START = 100  # Capture points: 100, 101, 102...
OBJID_VEHICLE_SPAWNERS_START = 1000  # Vehicle spawners: 1000+
OBJID_STATIONARY_EMPLACEMENTS_START = 2000  # Weapon emplacements: 2000+

# ==============================================================================
# Minimum Spawn Requirements (Portal validation)
# ==============================================================================

MIN_SPAWNS_PER_TEAM = 4  # Each team needs at least 4 spawn points

# ==============================================================================
# BF6 Vehicle Type Enum (from VehicleSpawner.gd)
# ==============================================================================

# Vehicle type enum indices for BF6 Portal VehicleSpawner nodes
# This enum is defined in the VehicleSpawner.gd script and must match exactly
BF6_VEHICLE_TYPE_ENUM = {
    "Abrams": 0,
    "Leopard": 1,
    "Cheetah": 2,
    "CV90": 3,
    "Gepard": 4,
    "UH60": 5,
    "Eurocopter": 6,
    "AH64": 7,
    "Vector": 8,
    "Quadbike": 9,
    "Flyer60": 10,
    "JAS39": 11,
    "F22": 12,
    "F16": 13,
    "M2Bradley": 14,
    "SU57": 15,
}
