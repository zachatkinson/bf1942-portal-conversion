# Constants Package - DRY/SOLID Architecture

## Overview

This package provides a modular constants system following SOLID principles to eliminate magic numbers and hardcoded strings throughout the BF Portal conversion toolset.

## Why Modular Constants?

**Before (Anti-pattern)**:
```python
# Hardcoded magic numbers scattered throughout codebase
lines.append('[node name="HQ_Team1" parent="TEAM_1_HQ" instance=ExtResource("8")]')
lines.append("height = 50.0")
lines.append("ObjId = 1")
```

**After (DRY/SOLID)**:
```python
# Single source of truth via constants
lines.append(f'[node name="HQ_Team1" parent="TEAM_1_HQ" instance=ExtResource("{EXT_RESOURCE_POLYGON_VOLUME}")]')
lines.append(f"height = {HQ_PROTECTION_HEIGHT_M}")
lines.append(f"ObjId = {OBJID_HQ_START}")
```

### Benefits

1. **Single Responsibility**: Each module focuses on one domain
2. **DRY (Don't Repeat Yourself)**: No duplicated magic numbers
3. **Maintainability**: Easy to find and update constants
4. **Type Safety**: Constants are defined once with clear types
5. **Self-Documenting**: Constant names explain their purpose
6. **Prevents Bugs**: Changing a constant updates all usages automatically

## Module Structure

### `extresource_ids.py` - Godot ExtResource IDs

**Purpose**: Define ExtResource IDs for Portal SDK scenes.

**Constants**:
- `EXT_RESOURCE_HQ_SPAWNER = "1"`
- `EXT_RESOURCE_SPAWN_POINT = "2"`
- `EXT_RESOURCE_CAPTURE_POINT = "3"`
- `EXT_RESOURCE_VEHICLE_SPAWNER = "4"`
- `EXT_RESOURCE_STATIONARY_EMPLACEMENT = "5"`
- `EXT_RESOURCE_COMBAT_AREA = "6"`
- `EXT_RESOURCE_TERRAIN = "7"`
- `EXT_RESOURCE_POLYGON_VOLUME = "8"`
- `EXT_RESOURCE_STATIC_ASSETS_START = 9`

**Critical**: These IDs MUST match the order in `TscnGenerator._init_ext_resources()`.

### `scene_paths.py` - Portal SDK Scene Paths

**Purpose**: Define `res://` paths to Portal SDK `.tscn` scene files.

**Constants**:
- `SCENE_PATH_HQ_SPAWNER`
- `SCENE_PATH_SPAWN_POINT`
- `SCENE_PATH_CAPTURE_POINT`
- `SCENE_PATH_VEHICLE_SPAWNER`
- `SCENE_PATH_STATIONARY_EMPLACEMENT`
- `SCENE_PATH_COMBAT_AREA`
- `SCENE_PATH_POLYGON_VOLUME`
- `SCENE_PATH_TERRAIN_FORMAT` (dynamic, use with `.format(base_terrain=...)`)

### `gameplay.py` - Gameplay Values

**Purpose**: Define gameplay-related values (HQ zones, capture areas, spawn requirements, etc.)

**Constants**:
- `HQ_PROTECTION_RADIUS_M = 50.0` - HQ safety zone radius
- `HQ_PROTECTION_HEIGHT_M = 50.0` - HQ safety zone height
- `COMBAT_AREA_HEIGHT_M = 200.0` - Vertical extent of combat zone
- `COMBAT_AREA_EXCLUSION_ZONE_M = 20.0` - Inset from terrain edges
- `CAPTURE_ZONE_HEIGHT_M = 50.0` - Capture zone trigger height
- `OBJID_HQ_START = 1` - Team HQs object IDs
- `OBJID_CAPTURE_POINTS_START = 100` - Capture points object IDs
- `OBJID_VEHICLE_SPAWNERS_START = 1000` - Vehicle spawner object IDs
- `OBJID_STATIONARY_EMPLACEMENTS_START = 2000` - Weapon emplacement object IDs
- `MIN_SPAWNS_PER_TEAM = 4` - Minimum spawn points required per team

### `terrain.py` - Terrain Calibration

**Purpose**: Define terrain-specific calibration values and defaults.

**Constants**:
- `DEFAULT_MAP_SIZE_M = 2048.0` - Default map size if no bounds provided
- `DEFAULT_CENTER_HEIGHT_M = 80.0` - Default Y position for combat area center
- `MP_TUNGSTEN_MESH_CENTER_X = 59.0` - MP_Tungsten mesh center X
- `MP_TUNGSTEN_MESH_CENTER_Z = -295.0` - MP_Tungsten mesh center Z
- `MP_TUNGSTEN_ROTATED_OFFSET_X = 295.0` - Post-rotation translation X
- `MP_TUNGSTEN_ROTATED_OFFSET_Z = 59.0` - Post-rotation translation Z

### `file_format.py` - File Format & Asset Filtering

**Purpose**: Define `.tscn` file format values and asset filtering rules.

**Constants**:
- `TSCN_FORMAT_VERSION = 3` - Godot 4 .tscn format version
- `TSCN_SCENE_TYPE = "gd_scene"`
- `GAMEPLAY_KEYWORDS = [...]` - Keywords to exclude from static layer
- `DEBUG_ASSET_LOG_LIMIT = 5` - Max assets to log debug info for

### `validation.py` - Validation Messages

**Purpose**: Define standardized validation error messages.

**Constants**:
- `ERROR_MISSING_TEAM1_HQ`
- `ERROR_MISSING_TEAM2_HQ`
- `ERROR_INSUFFICIENT_TEAM1_SPAWNS`
- `ERROR_INSUFFICIENT_TEAM2_SPAWNS`
- `ERROR_FILE_NOT_FOUND`

## Usage

### Import Everything (Convenience)

```python
from .constants import *

# All constants available
lines.append(f'instance=ExtResource("{EXT_RESOURCE_HQ_SPAWNER}")')
lines.append(f"height = {HQ_PROTECTION_HEIGHT_M}")
```

### Import Specific Modules (Best Practice)

```python
from .constants.extresource_ids import EXT_RESOURCE_HQ_SPAWNER, EXT_RESOURCE_SPAWN_POINT
from .constants.gameplay import HQ_PROTECTION_HEIGHT_M, MIN_SPAWNS_PER_TEAM

# Only imported constants available (clearer dependencies)
```

### Import Specific Constants (Most Explicit)

```python
from .constants.gameplay import HQ_PROTECTION_HEIGHT_M

# Only specific constant available (maximum clarity)
```

## Adding New Constants

1. **Choose the Right Module**: Determine which domain the constant belongs to
2. **Add to Module**: Define the constant with a descriptive name and docstring
3. **Update `__init__.py`**: Add to `__all__` list for convenience imports
4. **Update Usage**: Replace hardcoded values with the new constant
5. **Document**: Add to this README if it's a commonly-used constant

Example:
```python
# In constants/gameplay.py
RESPAWN_DELAY_SECONDS = 10.0  # Default respawn delay in seconds

# In constants/__init__.py
from .gameplay import RESPAWN_DELAY_SECONDS
__all__ = [..., "RESPAWN_DELAY_SECONDS"]

# Usage
delay = RESPAWN_DELAY_SECONDS
```

## Best Practices

### DO:
✅ Use constants for all magic numbers and strings
✅ Name constants descriptively (e.g., `HQ_PROTECTION_RADIUS_M`, not `RADIUS`)
✅ Include units in constant names (e.g., `_M` for meters, `_SECONDS` for time)
✅ Group related constants in the same module
✅ Document what each constant represents
✅ Use UPPER_CASE for constants

### DON'T:
❌ Hardcode magic numbers directly in code
❌ Use vague constant names (e.g., `CONSTANT1`, `VALUE`)
❌ Mix unrelated constants in the same module
❌ Forget to update `__all__` when adding constants
❌ Use mutable types for constants (use tuples, not lists)

## Maintenance

When updating constants:

1. **Search for Usages**: Before changing, search for all usages
2. **Update Comments**: Update any comments referencing the old value
3. **Test Thoroughly**: Regenerate test maps to verify changes
4. **Document Reason**: Add a comment explaining why the value changed

## Example: The Bug This Fixed

**Problem**: Adding `StationaryEmplacementSpawner` as ExtResource ID 5 shifted all subsequent IDs, but hardcoded strings throughout the code still used old IDs.

**Result**: PolygonVolume nodes were incorrectly instancing terrain meshes, causing visual corruption.

**Solution**: Constants package ensures IDs are defined once and used consistently.

```python
# Before (Brittle - caused bug)
lines.append('[node name="HQ_Team1" instance=ExtResource("8")]')  # Breaks if IDs change!

# After (Robust - automatically adapts)
lines.append(f'[node name="HQ_Team1" instance=ExtResource("{EXT_RESOURCE_POLYGON_VOLUME}")]')
```

## Future Extensions

Potential new constant modules:

- `asset_paths.py` - File system paths (FbExportData, GodotProject, etc.)
- `vehicle_mappings.py` - Vehicle type enum mappings
- `weapon_mappings.py` - Weapon type mappings
- `network.py` - Network/multiplayer constants
- `physics.py` - Physics-related constants

---

**Last Updated**: 2025-10-13
**Author**: Zach Atkinson
**AI Assistant**: Claude (Anthropic)
