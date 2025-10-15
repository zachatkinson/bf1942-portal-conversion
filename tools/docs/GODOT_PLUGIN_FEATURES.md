# Godot Plugin Feature Specification

**Last Updated**: 2025-10-13
**Status**: Design Document - Not Yet Implemented

## Overview

This document outlines planned features for the Godot editor plugin to support Portal map development. These features provide visual feedback and manual control over map elements, keeping editorial decisions in the hands of the user.

---

## Feature 1: Manual Object Culling

### Purpose
Allow users to manually identify and remove out-of-bounds objects with visual feedback, rather than automatically removing them during conversion.

### Rationale
**Why Manual Instead of Automatic?**

1. **User Control**: Developer can see what will be removed before committing to the change
2. **Context-Aware**: Some "out-of-bounds" objects may be intentional (e.g., distant trees for atmosphere)
3. **Visual Feedback**: Red/yellow highlighting shows exactly which objects are affected
4. **Debugging**: Helps identify why certain objects might be positioned incorrectly
5. **Prevents Centroid Issues**: Automatic culling during conversion can affect asset centering calculations

### User Interface

**Location**: Godot editor → BFPortal panel → "Tools" section

**Button**: "Cull Out-of-Bounds Objects"

**Workflow**:
1. User clicks "Cull Out-of-Bounds Objects" button
2. Plugin scans all objects in `Static` layer
3. Plugin checks each object's position against terrain bounds
4. Out-of-bounds objects are highlighted in viewport:
   - **Red**: Far outside bounds (>20m)
   - **Yellow**: Slightly outside bounds (<20m)
5. Dialog shows:
   ```
   Found 23 objects outside terrain bounds:
   - 15 far out (>20m from edge)
   - 8 slightly out (<20m from edge)

   [Remove All] [Select for Review] [Cancel]
   ```

**Options**:
- **Remove All**: Immediately deletes all out-of-bounds objects
- **Select for Review**: Selects out-of-bounds objects in scene tree for manual review
- **Cancel**: Clears highlighting and takes no action

### Technical Implementation

**GDScript Pseudocode**:
```gdscript
func cull_out_of_bounds_objects():
    # Get terrain bounds from terrain node
    var terrain = get_node("Static/MP_Tungsten_Terrain")
    var terrain_bounds = get_terrain_bounds(terrain)  # Returns AABB

    # Find Static layer
    var static_layer = get_node("Static")
    if not static_layer:
        push_error("No Static layer found")
        return

    # Scan all children (except terrain itself)
    var out_of_bounds = []
    for child in static_layer.get_children():
        if "_Terrain" in child.name:
            continue  # Skip terrain node

        var pos = child.global_position
        var distance_outside = calculate_distance_outside_bounds(pos, terrain_bounds)

        if distance_outside > 0:
            out_of_bounds.append({
                "node": child,
                "distance": distance_outside,
                "position": pos
            })

    if out_of_bounds.is_empty():
        show_message("All objects are within terrain bounds!")
        return

    # Highlight objects
    for item in out_of_bounds:
        var color = Color.YELLOW if item.distance < 20.0 else Color.RED
        highlight_node(item.node, color)

    # Show dialog
    var dialog = preload("res://addons/bfportal/CullDialog.tscn").instantiate()
    dialog.set_out_of_bounds_objects(out_of_bounds)
    dialog.connect("remove_all_pressed", _on_remove_all)
    dialog.connect("select_for_review_pressed", _on_select_for_review)
    dialog.connect("cancel_pressed", _on_cull_cancel)
    add_child(dialog)

func _on_remove_all(objects: Array):
    for item in objects:
        item.node.queue_free()
    clear_highlights()
    show_message("Removed %d out-of-bounds objects" % objects.size())

func _on_select_for_review(objects: Array):
    EditorInterface.get_selection().clear()
    for item in objects:
        EditorInterface.get_selection().add_node(item.node)
    show_message("Selected %d objects for review" % objects.size())

func _on_cull_cancel():
    clear_highlights()
```

### Benefits
- ✅ **No Surprises**: User sees exactly what will be removed
- ✅ **Flexible**: Can choose to keep some "out-of-bounds" objects
- ✅ **Educational**: User learns terrain boundaries and object placement
- ✅ **Debugging Aid**: Helps identify coordinate transformation issues

---

## Feature 2: Terrain Snapping Tool

### Purpose
Manually snap selected objects to terrain surface with visual feedback.

### User Interface

**Location**: BFPortal panel → "Tools" section

**Button**: "Snap to Terrain"

**Workflow**:
1. User selects one or more objects in scene tree
2. User clicks "Snap to Terrain" button
3. Plugin adjusts Y position of each object to terrain surface
4. Shows summary: "Snapped 15 objects to terrain surface"

### Technical Implementation

**GDScript Pseudocode**:
```gdscript
func snap_to_terrain():
    var terrain = get_node("Static/MP_Tungsten_Terrain")
    if not terrain:
        push_error("No terrain found")
        return

    var terrain_provider = create_terrain_provider(terrain)
    var selected_nodes = EditorInterface.get_selection().get_selected_nodes()

    if selected_nodes.is_empty():
        show_message("No objects selected. Select objects first, then click Snap to Terrain.")
        return

    var snapped_count = 0
    for node in selected_nodes:
        if node is Node3D:
            var pos = node.global_position
            var terrain_height = terrain_provider.get_height_at_position(pos.x, pos.z)
            node.global_position.y = terrain_height
            snapped_count += 1

    show_message("Snapped %d objects to terrain" % snapped_count)
```

---

## Feature 3: Object Alignment Tools

### Purpose
Quickly align and distribute objects for level design.

### Tools

**Align Selected**:
- Align X: Align all selected objects to same X coordinate
- Align Y: Align all selected objects to same Y coordinate (height)
- Align Z: Align all selected objects to same Z coordinate

**Distribute Selected**:
- Distribute Evenly: Space selected objects evenly between first and last
- Grid Placement: Arrange objects in a grid pattern

### User Interface
**Location**: BFPortal panel → "Alignment" section

---

## Feature 4: Asset Validator

### Purpose
Validate map before export to catch common issues.

### Validation Checks

**Required Elements**:
- ✅ TEAM_1_HQ exists with ≥4 spawns
- ✅ TEAM_2_HQ exists with ≥4 spawns
- ✅ CombatArea exists with valid polygon
- ✅ Terrain exists in Static layer

**Quality Checks**:
- ⚠️ Spawns too close together (<5m)
- ⚠️ Spawns clipping through terrain
- ⚠️ Objects far outside Combat Area
- ⚠️ Missing asset scenes (placeholder Node3D)

### User Interface
**Button**: "Validate Map"

**Output**: Prints report to Godot console with clickable links to problem nodes

---

## Feature 5: Quick Test Mode

### Purpose
Quickly test map layout without full export.

### Features
- Generate preview .spatial.json
- Open in basic 3D viewer (if available)
- Show combat area boundaries in-game
- Spawn point visualization

---

## Implementation Priority

1. **High Priority**: Manual Object Culling (most requested, solves immediate pain point)
2. **Medium Priority**: Terrain Snapping Tool (useful for manual adjustments)
3. **Medium Priority**: Asset Validator (quality of life, prevents errors)
4. **Low Priority**: Object Alignment Tools (nice-to-have)
5. **Low Priority**: Quick Test Mode (requires external tooling)

---

## Integration with Conversion Pipeline

**Separation of Concerns**:
- **Conversion Pipeline** (`portal_convert.py`): Data transformation only
  - Parse BF1942 → Map assets → Transform coordinates → Adjust heights → Generate .tscn
  - NO editorial decisions (culling, filtering, etc.)

- **Godot Plugin**: Editorial decisions with visual feedback
  - Manual culling with highlighting
  - Terrain snapping with preview
  - Validation with detailed reports

**Benefits**:
- Clean separation between automated transformation and manual editing
- User maintains full control over final map composition
- Visual feedback prevents mistakes
- Easier to debug (clear which tool did what)

---

## Future Enhancements

**Advanced Culling Options**:
- Cull by asset type (e.g., "Remove all trees outside bounds")
- Cull by distance threshold (e.g., "Remove objects >50m outside")
- Smart culling (e.g., "Keep objects that contribute to skyline")

**Batch Operations**:
- Replace all instances of asset A with asset B
- Randomize tree/rock varieties
- Auto-distribute spawns evenly around HQ

**Visual Aids**:
- Show combat area boundaries in viewport
- Show HQ protection zones
- Show capture point radii
- Heatmap of object density

---

*This document will be updated as features are implemented and user feedback is collected.*
