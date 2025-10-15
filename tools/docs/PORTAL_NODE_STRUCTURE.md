# Portal Node Structure Reference

**Date**: 2025-10-13
**Purpose**: Document the correct structure for Portal gameplay nodes based on SDK analysis

---

## HQ_PlayerSpawner (Team Headquarters)

### Required Properties
```gdscript
Team = 1  # or 2
AltTeam = 0  # Alternative team assignment
ObjId = 1  # Unique identifier
HQArea = NodePath("HQ_Team1")  # Reference to PolygonVolume child
InfantrySpawns = [NodePath("SpawnPoint_1_1"), ...]  # Array of spawn point references
```

### Required Children
1. **HQ Area (PolygonVolume)**: Defines protected spawn zone
   - Type: PolygonVolume instance
   - Name pattern: `HQ_Team1`, `HQ_Team2`
   - Properties:
     - `height`: Vertical extent (typically 50.0)
     - `points`: PackedVector2Array defining horizontal boundary

2. **Spawn Points (4+ required per HQ)**:
   - Type: SpawnPoint instances
   - Name pattern: `SpawnPoint_1_1`, `SpawnPoint_1_2`, etc.
   - Must be children of HQ_PlayerSpawner
   - Must be referenced in `InfantrySpawns` array

### Example Structure
```
TEAM_1_HQ (HQ_PlayerSpawner)
├── HQ_Team1 (PolygonVolume)
├── SpawnPoint_1_1
├── SpawnPoint_1_2
├── SpawnPoint_1_3
└── SpawnPoint_1_4
```

---

## CapturePoint (Conquest Objectives)

### Required Properties
```gdscript
Team = 0  # Initial owner (0 = neutral)
ObjId = 101  # Unique identifier
InfantrySpawnPoints_Team1 = [NodePath(...), ...]  # Team 1 spawn points (≥3)
InfantrySpawnPoints_Team2 = [NodePath(...), ...]  # Team 2 spawn points (≥3)
```

### Required Children
1. **Capture Zone (PolygonVolume)**: Defines capture area
   - Type: PolygonVolume instance
   - Name pattern: `CaptureZone_1`, `CaptureZone_2`, etc.
   - Properties:
     - `height`: Vertical extent (typically 50.0)
     - `points`: PackedVector2Array defining capture boundary

2. **Spawn Points (3+ per team)**:
   - Type: SpawnPoint instances
   - Name pattern: `CP1_Spawn_1_1`, `CP1_Spawn_2_1`, etc.
   - Must be children of CapturePoint
   - Must be referenced in spawn arrays

### Example Structure
```
CapturePoint_1
├── CaptureZone_1 (PolygonVolume)
├── CP1_Spawn_1_1 (Team 1)
├── CP1_Spawn_1_2 (Team 1)
├── CP1_Spawn_1_3 (Team 1)
├── CP1_Spawn_2_1 (Team 2)
├── CP1_Spawn_2_2 (Team 2)
└── CP1_Spawn_2_3 (Team 2)
```

---

## CombatArea (Playable Boundary)

### Required Properties
```gdscript
CombatVolume = NodePath("CombatVolume")  # Reference to PolygonVolume child
```

### Required Children
1. **Combat Volume (PolygonVolume)**: Defines out-of-bounds boundary
   - Type: PolygonVolume instance
   - Name: `CombatVolume` or `CollisionPolygon3D`
   - Properties:
     - `height`: Vertical extent (typically 100.0)
     - `points`: PackedVector2Array defining playable boundary

### Example Structure
```
CombatArea
└── CombatVolume (PolygonVolume)
```

---

## SpawnPoint (Player Spawn Location)

### Properties
- Transform defines position and rotation (facing direction)
- No required properties
- Always a child of HQ_PlayerSpawner or CapturePoint

### Transform Notes
- Position: Where player spawns
- Rotation: Direction player faces when spawning
- Example: `Transform3D(rotation_matrix, x, y, z)`

---

## Validation Checklist

### Minimum Requirements for Valid Portal Map

**Team HQs**:
- ✅ TEAM_1_HQ exists
- ✅ TEAM_1_HQ has HQArea (PolygonVolume child)
- ✅ TEAM_1_HQ has ≥4 spawn points
- ✅ TEAM_2_HQ exists
- ✅ TEAM_2_HQ has HQArea (PolygonVolume child)
- ✅ TEAM_2_HQ has ≥4 spawn points

**Combat Area**:
- ✅ CombatArea exists
- ✅ CombatArea has CombatVolume (PolygonVolume child)

**Static Layer**:
- ✅ Static layer exists
- ✅ Terrain mesh present in Static layer

**Capture Points (if Conquest mode)**:
- ✅ Each CapturePoint has CaptureZone (PolygonVolume child)
- ✅ Each CapturePoint has ≥3 Team 1 spawn points
- ✅ Each CapturePoint has ≥3 Team 2 spawn points

---

## Common Mistakes

### ❌ Wrong: CaptureVolume Property
```gdscript
# DON'T: CapturePoints don't have CaptureVolume property
CaptureVolume = NodePath("...")
```

### ✅ Correct: CaptureZone Child Node
```gdscript
# DO: CapturePoints have CaptureZone child
[node name="CaptureZone_1" parent="CapturePoint_1" instance=...]
```

### ❌ Wrong: Direct NodePath Usage
```gdscript
# DON'T: Pass object directly to get_node_or_null()
var node = parent.get_node_or_null(some_object)
```

### ✅ Correct: NodePath Constructor
```gdscript
# DO: Wrap with NodePath() constructor for safety
var path = parent.get("HQArea")
var node = parent.get_node_or_null(NodePath(path))
```

---

## References

- **SDK Docs**: `/PortalSDK/sdk_reference/index.html`
- **Example Map**: `/PortalSDK/GodotProject/levels/Kursk.tscn`
- **Validation Code**: `/PortalSDK/GodotProject/addons/bf1942_tools/bf1942_tools.gd:443` (`_on_validate_map()`)

---

*This document is based on analysis of the official Portal SDK and working example maps.*
