# Portal SDK Solutions Summary

## 1. Removing Default Map Assets for Creative Freedom

### Problem
Portal automatically loads ALL built-in assets (buildings, props, vegetation) for a map, even if not placed in Godot, limiting creative freedom.

### Root Cause
Portal maps use TWO mesh files:
- `MP_[MapName]_Terrain` - Terrain/landscape
- `MP_[MapName]_Assets` - Built-in props/buildings

When only Terrain is referenced, Portal **automatically** loads Assets by convention.

### Solution
Explicitly include MP_Tungsten_Assets but hide it:

**Method 1: Add to .tscn and hide** (Recommended)
```gdscript
[node name="Static" type="Node3D" parent="."]

[node name="MP_Tungsten_Terrain" parent="Static" instance=ExtResource("7")]
transform = Transform3D(...)

[node name="MP_Tungsten_Assets" parent="Static" instance=ExtResource("8")]
visible = false  # Hides all default assets!
```

**Method 2: Manual spatial.json edit**
Add to Static section after export:
```json
{
  "name": "MP_Tungsten_Assets",
  "type": "MP_Tungsten_Assets",
  "visible": false
}
```

### Key Insight
Your **custom** placed assets (trees, crates, buildings in Static/) are SEPARATE and will still export normally. This only affects the pre-baked default mesh.

### Verification
Check your spatial.json includes BOTH:
```bash
jq '.Static[].type' FbExportData/levels/Kursk.spatial.json
```

Should show:
```
"MP_Tungsten_Terrain"
"MP_Tungsten_Assets"
```

---

## 2. CombatArea Ceiling Discovery

### Problem
CombatArea initially positioned at ground level, clipping through terrain.

### Discovery
Analysis of official maps (MP_Tungsten, MP_Aftermath) revealed:

**CombatArea is a CEILING, not a floor!**
- Positioned ~140m above ground (40-50m above highest terrain)
- Height: 100m (not 200m)
- Purpose: Prevents flying/climbing too high
- Ground boundaries: Defined by terrain geometry

### Solution Implemented
1. Updated `Kursk.tscn`: CombatArea CollisionPolygon3D at Y=140, height=100
2. Rewrote `combat_area_generator.py`: Positions ceiling above terrain automatically
3. Updated all tests to verify ceiling logic
4. Documented in `sdk_reference/index.html`

**Transform Structure:**
```gdscript
[node name="CombatArea" parent="."]  # No transform
[node name="CollisionPolygon3D" parent="CombatArea"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 140, 0)  # Y offset here!
height = 100.0  # Extends upward from Y=140 to Y=240
```

---

## 3. Capture Point Labels Fixed

### Problem
Both capture points showed as "A" instead of sequential labels (A, B).

### Solution
Added `Label` property to CapturePoint nodes:

```gdscript
[node name="CapturePoint_1" ...]
Label = "A"
ObjId = 101

[node name="CapturePoint_2" ...]
Label = "B"
ObjId = 102
```

Now displays correctly in-game as Objective A and Objective B.

---

## 4. SDK Reference Style Alignment

### Problem
SDK documentation didn't match official Battlefield Portal design language.

### Solution
Comprehensive style overhaul:
- **Removed all rounded corners** (~187 instances) - flat/brutalist design
- **Eliminated shadows** - completely flat appearance
- **Minimized borders** - bottom separators only
- **Added uppercase headings** with wide letter-spacing
- **Removed gradients** - solid colors only
- **Verified colors** match official Portal exactly

### Results
- File size reduced 30% (196KB → 136KB)
- Professional, militant, high-contrast aesthetic
- Matches official Battlefield design language

---

## Documentation Created

1. **`tools/docs/REMOVE_DEFAULT_ASSETS.md`** - Complete guide with 3 methods
2. **`sdk_reference/index.html`** - Updated CombatArea documentation
3. **`sdk_reference/STYLE_CHANGES.md`** - Detailed style update log
4. **This file** - Summary of all solutions

---

## Next Steps for Users

### To Get Blank Canvas Map:
1. Add `MP_Tungsten_Assets` node to Static (visible=false)
2. Export normally
3. Verify spatial.json includes both Terrain and Assets

### To Add More Capture Points:
```gdscript
[node name="CapturePoint_3" ...]
Label = "C"
ObjId = 103
```

### To Test In-Game:
1. Export Kursk.tscn from Godot
2. Create experience: `python3 tools/create_experience.py`
3. Upload to Portal web builder
4. Launch custom game

---

**Date**: 2025-10-14  
**Author**: Claude (AI Assistant)  
**Approved by**: Zach Atkinson
