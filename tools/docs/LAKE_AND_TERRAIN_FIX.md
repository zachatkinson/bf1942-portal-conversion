# Lake Assets and Terrain Alignment Fix

## Issues Identified

### 1. Lake Asset Scaling
**Problem**: BF1942 Kursk has 3 large lakes (40-117m dimensions) that were mapped to small puddle decals and likely culled as out-of-bounds.

**Original BF1942 Lake Dimensions**:
- **Lake 1** (at X=632.37, Z=349.64): 55.30m x 101.95m (3,640 m²)
- **Lake 2** (at X=616.54, Z=719.80): 57.31m x 84.19m (3,485 m²)
- **Lake 3** (at X=446.83, Z=836.27): 40.34m x 116.86m (2,214 m²)

**Portal Mapping**:
- `lake` → `Decal_PuddleLong_01`
- `lake2` → `Decal_PuddleLong_02`
- `lake3` → `Decal_PuddleLong_06`

**Issue**: Puddle decals are ~5-10m, not 40-117m. Need significant scaling.

### 2. Floating Assets
**Problem**: Non-tree, non-spawn assets not properly aligned to terrain height, causing objects to float above ground.

**Root Cause**: Y-coordinate (height) from BF1942 doesn't match Portal/Tungsten terrain elevation at same XZ position.

## Solutions

### Solution 1: Lake Asset Scaling

**Approach**: Apply Transform3D scale to puddle decals to match original lake dimensions.

**Steps**:
1. Calculate scale factors based on puddle default size vs BF1942 polygon bounds
2. Apply rotation to match lake orientation (currently using default orientation)
3. Position at correct world coordinates
4. Ensure within combat area boundaries

**Implementation** (in StaticLayerGenerator):

```python
def _generate_lake_with_scale(self, bf1942_type: str, portal_type: str,
                               transform: Transform, lake_dims: dict) -> str:
    """Generate lake with appropriate scaling.

    Args:
        bf1942_type: Original BF1942 lake type (lake, lake2, lake3)
        portal_type: Portal puddle decal type
        transform: World transform
        lake_dims: Dict with 'width' and 'height' in meters

    Returns:
        Scaled transform for puddle decal
    """
    # Assume puddle default is ~8m x 3m (need to verify in Godot)
    DEFAULT_PUDDLE_WIDTH = 8.0
    DEFAULT_PUDDLE_HEIGHT = 3.0

    scale_x = lake_dims['width'] / DEFAULT_PUDDLE_WIDTH
    scale_z = lake_dims['height'] / DEFAULT_PUDDLE_HEIGHT
    scale_y = 1.0  # Keep Y scale normal

    # Apply scale to transform
    transform.scale = Vector3(scale_x, scale_y, scale_z)

    return self.transform_formatter.format(transform)
```

**Lake Dimension Constants**:
```python
LAKE_DIMENSIONS = {
    'lake': {'width': 55.30, 'height': 101.95},
    'lake2': {'width': 57.31, 'height': 84.19},
    'lake3': {'width': 40.34, 'height': 116.86},
}
```

### Solution 2: Terrain Height Alignment

**Approach**: Query Portal terrain heightmap to get accurate Y coordinate for each object.

**Options**:

#### Option A: Godot Terrain Raycast (Recommended)
Use Godot's terrain collision to raycast downward from object position and find ground level.

**Implementation**:
1. Load Kursk.tscn in Godot
2. Run GDScript to raycast from each static object position
3. Export corrected heights to JSON
4. Re-import into Python generator

**GDScript** (tools/fix_terrain_heights.gd):
```gdscript
extends Node

func fix_static_object_heights():
    var static_layer = get_node("Static")
    var terrain = get_node("MP_Tungsten_Terrain")
    var space_state = get_world_3d().direct_space_state

    for child in static_layer.get_children():
        var pos = child.global_position

        # Raycast downward from high above object
        var query = PhysicsRayQueryParameters3D.create(
            Vector3(pos.x, 200, pos.z),  # Start high
            Vector3(pos.x, -100, pos.z)  # End low
        )

        var result = space_state.intersect_ray(query)
        if result:
            var ground_y = result.position.y
            child.global_position.y = ground_y
            print("Fixed %s: Y %.2f -> %.2f" % [child.name, pos.y, ground_y])
```

#### Option B: BF1942 Heightmap Extraction
Extract BF1942 Kursk heightmap, apply coordinate transform, use as reference.

**Cons**: Portal terrain is different from BF1942, so heights won't match exactly.

#### Option C: Manual Offset Calibration
Find average height difference between BF1942 and Portal terrain, apply uniform offset.

**Cons**: Doesn't account for terrain variation.

### Recommended Implementation Plan

**Phase 1: Lake Fix** (Quick Win)
1. Add `LAKE_DIMENSIONS` constant to mappings file
2. Update StaticLayerGenerator to detect lake assets
3. Apply scaling transform when generating lake nodes
4. Regenerate Kursk.tscn
5. Verify lakes appear and are correctly sized

**Phase 2: Terrain Alignment** (More Complex)
1. Load Kursk.tscn in Godot editor
2. Run terrain raycast script to fix all static object heights
3. Save corrected scene
4. Document process for future maps

**Phase 3: Automation** (Future Enhancement)
1. Integrate Godot terrain queries into Python pipeline
2. Auto-correct heights during initial generation
3. Requires Godot headless mode or GDExtension

## Testing Plan

### Lake Scaling Test
1. Generate Kursk with scaled lakes
2. Load in Godot editor
3. Verify:
   - Lakes visible on terrain
   - Correct size (measure in editor)
   - Within combat area
   - Positioned at correct XZ coordinates

### Terrain Alignment Test
1. Select 10 random static objects
2. Manually check Y position in Godot
3. Run raycast fix
4. Verify objects now sit on terrain
5. Check for edge cases (objects on slopes)

## Code Changes Required

### 1. Update bf1942_to_portal_mappings.json

Add scale metadata:
```json
"lake": {
  "bf1942_type": "lake",
  "portal_equivalent": "Decal_PuddleLong_01",
  "category": "terrain",
  "scale": {"width": 55.30, "height": 101.95},
  "notes": "Large lake - requires 7x scale",
  "manually_verified": true
}
```

### 2. Update StaticLayerGenerator

Add lake detection and scaling logic in `generate()` method.

### 3. Create Terrain Fix Tool

**tools/fix_terrain_heights.py**:
```python
#!/usr/bin/env python3
"""Fix floating assets by aligning to Portal terrain height."""

def load_kursk_tscn():
    """Load Kursk.tscn and parse static objects."""
    pass

def apply_terrain_heights(tscn_path, corrected_heights):
    """Apply corrected Y coordinates from Godot raycast."""
    pass

def export_for_godot_raycast(static_objects):
    """Export XZ positions for Godot to raycast."""
    pass
```

## Success Criteria

- [ ] All 3 lakes visible in Kursk map
- [ ] Lake sizes match BF1942 dimensions (±10%)
- [ ] Lakes positioned at correct world coordinates
- [ ] No static objects floating (Y offset < 0.5m)
- [ ] No static objects buried (visible above terrain)
- [ ] Process documented for future maps

## Notes

- Portal SDK doesn't support actual water bodies (swimming, physics)
- Lakes are purely visual using decal textures
- Terrain alignment may need manual tweaking for complex geometry
- Consider adding water sound zones at lake positions for immersion
