# BF1942 Tools for Godot

Tools for converting BF1942 maps to Battlefield Portal format.

## Terrain Snap Tools

Two buttons for snapping objects to terrain:

### 1. "Snap Selected to Terrain"
Snaps spawn points of selected HQ/CapturePoint nodes to terrain.

### 2. "Snap ALL to Terrain" ⭐ RECOMMENDED
Snaps **everything** in the scene to terrain:
- All HQs and their spawn points
- All CapturePoints and their spawn points
- All VehicleSpawners
- All StationaryEmplacements
- All static assets (trees, buildings, props, etc.)

### How to Use

1. **Enable the plugin** (first time only):
   - In Godot, go to `Project > Project Settings > Plugins`
   - Find "BF1942 Tools" and check the "Enable" checkbox
   - You should see a "Snap Spawns to Terrain" button in the 3D editor toolbar

2. **Open your map**:
   - Open `levels/Kursk.tscn` (or your map)

3. **Click the "Snap ALL to Terrain" button**:
   - The tool will snap everything to terrain automatically
   - Check the Godot Output console to see progress
   - You'll see grouped output for gameplay objects and static assets

4. **Save the scene** (Ctrl+S)

### Alternative: Snap Selected Only

If you only want to snap specific nodes:
1. Select `TEAM_1_HQ` or `CapturePoint_1` in scene tree
2. Click "Snap Selected to Terrain"
3. Only that node's children will be snapped

### What it Does

**"Snap ALL to Terrain"** processes:
1. **Auto-creates terrain collision** (if not already present)
   - Generates trimesh collision from terrain mesh
   - Uses it for physics raycasting
   - **Automatically removes it after snapping** (keeps file lean!)
2. **Root-level gameplay objects**: HQs, CapturePoints, VehicleSpawners, StationaryEmplacements
3. **Their children**: All spawn points (recursively)
4. **Static layer objects**: All props, trees, buildings in the Static layer

For each object:
- **Finds terrain**: Locates the terrain mesh in the Static layer
- **Raycasts downward**: Casts a ray from 1000m above straight down
- **Updates Y position**: Sets Y coordinate to match terrain height at that XZ position
- **Preserves X/Z**: Keeps original horizontal positions
- **Preserves hierarchy**: Doesn't move objects between layers or change parent-child relationships

### Technical Details

The tool:
- Only processes nodes with "SpawnPoint" or "Spawn" in their name
- Uses Godot's physics raycast system
- Updates positions in local coordinates (relative to parent)
- Preserves rotation and scale

### Workflow

**Before export to Portal:**
1. Generate map with `python3 tools/portal_convert.py --map Kursk`
2. Open in Godot
3. Click **"Snap ALL to Terrain"** button ⭐
4. Save scene (Ctrl+S)
5. Export via BFPortal panel

This ensures:
- All spawn points sit on terrain (even on hills/valleys)
- All gameplay objects (HQs, vehicles, emplacements) are at correct height
- All static props (trees, buildings) are grounded properly
- Everything exports correctly to Portal with proper hierarchy

### Example Output

```
🌍 Found terrain: MP_Tungsten_Terrain
🔧 Creating temporary collision mesh for snapping...
✅ Created trimesh collision (365209 triangles)
============================================================

📍 GAMEPLAY OBJECTS (Root Level)
------------------------------------------------------------
  ✓ TEAM_1_HQ: Y 77.49 → 77.52 (Δ0.03)
    ↳ SpawnPoint_1_1: Y 0.08 → 2.34 (Δ2.26)
    ↳ SpawnPoint_1_2: Y -0.02 → -1.15 (Δ-1.13)
    ↳ SpawnPoint_1_3: Y -0.02 → 3.67 (Δ3.69)
  ✓ TEAM_2_HQ: Y 67.23 → 67.45 (Δ0.22)
    ↳ SpawnPoint_2_1: Y 0.05 → 1.89 (Δ1.84)
  ✓ CapturePoint_1: Y 72.15 → 72.18 (Δ0.03)
    ↳ CP1_Spawn_1_1: Y -0.01 → 2.56 (Δ2.57)
  ✓ VehicleSpawner_1: Y 75.00 → 75.23 (Δ0.23)

🏗️  STATIC OBJECTS (Visual Assets)
------------------------------------------------------------
  ✓ Birch_01_L_1: Y 68.50 → 68.67 (Δ0.17)
  ✓ BulkBag_01_34: Y 71.20 → 71.34 (Δ0.14)
  ✓ CartWoodSmall_01_89: Y 73.10 → 73.28 (Δ0.18)
  ... (1463 more objects)

============================================================
✅ Snapped 1486 objects to terrain!
🧹 Removing temporary collision mesh (keeping file lean)...
✅ Cleanup complete!
💾 Don't forget to save the scene (Ctrl+S)
```

### No Manual Setup Required!

The tool **automatically**:
- ✅ Detects if terrain has collision
- ✅ Creates trimesh collision if needed
- ✅ Uses it for snapping
- ✅ Removes it afterward (keeps .tscn file clean)
- ✅ Preserves any existing collision you've manually created

**You don't need to manually create StaticBody3D or CollisionShape3D anymore!** Just click the button and everything happens automatically.
