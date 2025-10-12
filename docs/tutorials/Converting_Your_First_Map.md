# Converting Your First Map

> Step-by-step tutorial for converting a Battlefield 1942 map to BF6 Portal format

**Purpose:** Complete walkthrough for converting your first BF1942 map from extraction to in-game testing
**Last Updated:** October 2025
**Difficulty:** Beginner
**Time Required:** ~45 minutes

---

## Table of Contents

- [What You'll Learn](#what-youll-learn)
- [Prerequisites](#prerequisites)
- [Step 1: Set Up Your Environment](#step-1-set-up-your-environment)
- [Step 2: Extract BF1942 Map Files](#step-2-extract-bf1942-map-files)
- [Step 3: Choose Your Portal Base Terrain](#step-3-choose-your-portal-base-terrain)
- [Step 4: Run the Conversion](#step-4-run-the-conversion)
- [Step 5: Open in Godot](#step-5-open-in-godot)
- [Step 6: Verify the Conversion](#step-6-verify-the-conversion)
- [Step 7: Export to Portal Format](#step-7-export-to-portal-format)
- [Step 8: Test In-Game](#step-8-test-in-game)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

---

## What You'll Learn

By the end of this tutorial, you will:

- ✅ Extract BF1942 map files from RFA archives
- ✅ Choose an appropriate Portal base terrain
- ✅ Run the conversion pipeline
- ✅ Open and verify the converted map in Godot
- ✅ Export to `.spatial.json` format
- ✅ Test your map in BF6 Portal

**Example:** We'll convert **Kursk** from BF1942 to BF6 Portal using the MP_Tungsten base terrain.

---

## Prerequisites

### Required Software

- [x] **Python 3.13+** - Check with `python3 --version`
- [x] **Godot 4.3+** - [Installation Guide](../setup/Godot_Setup_Guide.md)
- [x] **Portal SDK** - Cloned repository with Portal SDK files
- [x] **BF1942 Game Files** - Original game or extracted maps

### Required Files

- [x] **BF1942 Maps** - Extracted RFA archives
- [x] **Asset Mappings** - `tools/asset_audit/bf1942_to_portal_mappings.json` (included)
- [x] **Portal Asset Catalog** - `FbExportData/asset_types.json` (included)

### Platform Notes

- **Windows:** Full support
- **macOS:** Full support (see [macOS Guide](../setup/macOS_Compatibility_Patch.md) for export workaround)
- **Linux:** Full support

---

## Step 1: Set Up Your Environment

### Verify Python Installation

```bash
python3 --version
# Should show: Python 3.13.x or higher
```

### Verify Portal SDK

```bash
cd PortalSDK

# Check asset catalog exists
ls FbExportData/asset_types.json

# Check asset mappings exist
ls tools/asset_audit/bf1942_to_portal_mappings.json

# Check Godot project exists
ls GodotProject/project.godot
```

**Expected:** All files should exist.

---

## Step 2: Extract BF1942 Map Files

### On Windows

1. **Download BGA (Battlefield Game Archive)**
   - Get from: https://github.com/yann-papouin/bga

2. **Extract Kursk map**
   ```
   # Open BGA tool
   # Navigate to: Bf1942/Archives/bf1942/levels/
   # Select: Kursk.rfa
   # Click: Extract All
   # Extract to: PortalSDK/bf1942_source/extracted/Bf1942/Archives/bf1942/Levels/Kursk/
   ```

### On macOS/Linux

Use Wine to run BGA:

```bash
# Install Wine (if needed)
brew install wine  # macOS
# or
sudo apt install wine  # Linux

# Run BGA via Wine
wine BGA.exe
```

### Verify Extraction

```bash
ls bf1942_source/extracted/Bf1942/Archives/bf1942/Levels/Kursk

# Should see:
# - Init.con
# - StaticObjects.con
# - Heightmap.raw
# - Conquest/ (directory)
```

> 📝 **Note:** If extraction fails, try these alternatives:
> - WinRFA tool
> - Pre-extracted maps from BF1942 modding community

---

## Step 3: Choose Your Portal Base Terrain

Portal has several base terrains. Choose based on your map's theme:

### Available Base Terrains

| Terrain | Theme | Best For |
|---------|-------|----------|
| **MP_Tungsten** | Flat, grassy plains | Open terrain maps (Kursk, El Alamein) |
| **MP_Outskirts** | Urban ruins | City maps (Stalingrad, Berlin) |
| **MP_Limestone** | Rocky desert | Desert maps (Wake Island, Iwo Jima) |
| **MP_Battery** | Coastal cliffs | Coastal maps (Omaha Beach) |
| **MP_Hourglass** | Sandy desert | Large desert maps |

**For Kursk:** We'll use **MP_Tungsten** (open plains, matches original terrain).

### View Available Terrains

```bash
# List Portal base terrains
ls GodotProject/static/Maps/

# Should show:
# - MP_Tungsten/
# - MP_Outskirts/
# - MP_Limestone/
# - MP_Battery/
# - etc.
```

---

## Step 4: Run the Conversion

### Basic Conversion

```bash
python3 tools/portal_convert.py --map Kursk --base-terrain MP_Tungsten
```

**What happens:**
1. **Parsing** - Reads BF1942 .con files
   ```
   Parsing Kursk map data...
   Found 1439 objects
   Found 24 spawn points
   Found 6 control points
   ```

2. **Asset Mapping** - Maps BF1942 assets to Portal equivalents
   ```
   Mapping assets...
   Mapped 1439/1510 objects (95.3%)
   71 assets skipped (water/terrain elements)
   ```

3. **Coordinate Transform** - Calculates offsets
   ```
   Calculating coordinate offsets...
   Map center: (512.0, 512.0)
   Offset: (-512.0, 0.0, -512.0)
   ```

4. **Height Adjustment** - Adjusts object heights to terrain mesh
   ```
   Adjusting heights to Portal terrain...
   Using MP_Tungsten terrain mesh for height data
   ```

5. **Scene Generation** - Creates .tscn file
   ```
   Generating Kursk.tscn...
   ✅ Conversion complete!
   Output: GodotProject/levels/Kursk.tscn
   ```

> 💡 **Note:** The conversion tool automatically loads the Portal terrain mesh (`.glb` file) to adjust object heights. No separate heightmap parameter is needed.

---

## Step 5: Open in Godot

### Launch Godot

1. **Open Godot 4**
2. **Import Project** (if first time)
   - Click "Import"
   - Navigate to `PortalSDK/GodotProject/`
   - Select `project.godot`
   - Click "Import & Edit"

3. **Wait for initial import** (2-5 minutes first time)

### Open Your Map

1. **FileSystem panel** → `res://levels/`
2. **Double-click** `Kursk.tscn`
3. **Wait for scene to load**

**Expected:** 3D viewport shows terrain with placed objects.

---

## Step 6: Verify the Conversion

### Check Scene Structure

In the **Scene Tree** panel, verify:

```
Kursk (Node3D)
├── TEAM_1_HQ (HQ_PlayerSpawner)
│   ├── HQ_Team1 (PolygonVolume)
│   ├── SpawnPoint_1_1 (SpawnPoint)
│   ├── SpawnPoint_1_2 (SpawnPoint)
│   └── ... (more spawn points)
├── TEAM_2_HQ (HQ_PlayerSpawner)
│   ├── HQ_Team2 (PolygonVolume)
│   ├── SpawnPoint_2_1 (SpawnPoint)
│   └── ... (more spawn points)
├── CombatArea (CombatArea)
│   └── CollisionPolygon3D (PolygonVolume)
└── Static (Node3D)
    ├── MP_Tungsten_Terrain (Terrain)
    └── ... (static objects)
```

> ✅ **Good Sign:** All nodes present, no red "!" errors

### Inspect Spawn Points

1. **Select** `TEAM_1_HQ` in Scene Tree
2. **Inspector panel** → Check:
   - `Team` = 1 (Axis)
   - `InfantrySpawns` lists 4+ spawn points
   - `HQArea` references PolygonVolume

3. **Repeat for** `TEAM_2_HQ`

### Check Object Placements

1. **3D Viewport** → Navigate around map
   - **Middle mouse** = Rotate camera
   - **Scroll wheel** = Zoom
   - **Shift + Middle mouse** = Pan

2. **Look for issues:**
   - ❌ Objects floating in air?
   - ❌ Objects underground?
   - ❌ Objects outside CombatArea?
   - ✅ Objects on terrain surface?

> ⚠️ **If objects are floating/underground:** See [Troubleshooting](#objects-floatingunderground)

### Verify CombatArea

1. **Select** `CombatArea` → `CollisionPolygon3D`
2. **Top view** (View → Top)
3. **Check:** Polygon encloses all objects

---

## Step 7: Export to Portal Format

### Using Godot (Windows/Linux)

1. **BFPortal tab** (right panel or top menu)
2. **Click** "Export Current Level"
3. **Choose output location** (default: `FbExportData/levels/`)
4. **Wait for export** (~30 seconds)

**Expected:** `FbExportData/levels/Kursk.spatial.json` created

### Using Manual Script (macOS)

```bash
cd PortalSDK

python3 code/gdconverter/src/gdconverter/export_tscn.py \
    GodotProject/levels/Kursk.tscn \
    FbExportData \
    FbExportData/levels
```

**See:** [macOS Compatibility Guide](../setup/macOS_Compatibility_Patch.md) for details.

### Verify Export

```bash
# Check file exists and is valid JSON
ls -lh FbExportData/levels/Kursk.spatial.json

# Validate JSON
python3 -c "import json; json.load(open('FbExportData/levels/Kursk.spatial.json')); print('✅ Valid JSON')"
```

**Expected:**
- File size: 500KB - 5MB
- Valid JSON (no errors)

---

## Step 8: Test In-Game

### Upload to Portal Builder

1. **Open** BF6 Portal web builder
2. **Create new experience**
3. **Upload** `Kursk.spatial.json`
4. **Configure game mode** (Conquest recommended)
5. **Publish** experience

### Test Your Map

1. **Launch** Battlefield 6
2. **Portal → Browse → Your Experiences**
3. **Play** your converted Kursk map
4. **Check:**
   - Spawn points work?
   - Objects placed correctly?
   - Gameplay feels authentic?

---

## Troubleshooting

### Conversion Fails

**Error:** `Map directory not found`

**Cause:** BF1942 map not extracted or wrong path.

**Solution:**
```bash
# Verify extraction
ls bf1942_source/extracted/Bf1942/Archives/bf1942/Levels/Kursk/

# If missing, re-extract RFA archive
```

---

### Objects Floating/Underground

**Cause:** Terrain mesh mismatch or missing `.glb` terrain file.

**Solution:**
```bash
# Verify terrain mesh exists
ls GodotProject/raw/models/MP_Tungsten_Terrain.glb

# If missing, ensure Portal SDK is properly set up
```

Or try a different base terrain:
```bash
# Rebase to different terrain (preserves horizontal positions)
python3 tools/portal_rebase.py \
    --input GodotProject/levels/Kursk.tscn \
    --output GodotProject/levels/Kursk_battery.tscn \
    --new-base MP_Battery
```

---

### Asset Mapping Warnings

**Warning:** `Asset 'PineTree' not available on MP_Tungsten, using fallback 'BirchTree'`

**Cause:** Portal asset has `levelRestrictions` and isn't available on target terrain.

**Solution:** This is normal. The system automatically uses fallbacks. Review console output to see which assets were substituted.

---

### Export Fails in Godot

**Error:** "Export failed" or empty `.spatial.json`

**Solutions:**
1. **Check console** (bottom panel) for errors
2. **Verify BFPortal plugin enabled:**
   - Project → Project Settings → Plugins
   - Enable "BF Portal"
   - Restart Godot

3. **Try manual export** (macOS users - see Step 7)

---

### Scene Won't Open in Godot

**Error:** "Failed to load resource" errors

**Cause:** Portal SDK assets missing.

**Solution:**
```bash
# Verify Portal SDK files
ls GodotProject/raw/models/
# Should contain many .glb files

# If missing, download full Portal SDK from EA/DICE
```

---

## Next Steps

### You've Successfully Converted Your First Map! 🎉

**What to try next:**

1. **Convert more maps**
   ```bash
   python3 tools/portal_convert.py --map Wake_Island --base-terrain MP_Limestone
   python3 tools/portal_convert.py --map El_Alamein --base-terrain MP_Hourglass
   ```

2. **Try different base terrains**
   ```bash
   # Rebase existing map to new terrain (fast!)
   python3 tools/portal_rebase.py \
       --input GodotProject/levels/Kursk.tscn \
       --output GodotProject/levels/Kursk_outskirts.tscn \
       --new-base MP_Outskirts
   ```

3. **Customize asset mappings**
   - Edit `tools/asset_audit/bf1942_to_portal_mappings.json`
   - Change Portal equivalents
   - Re-run conversion

4. **Study the Kursk case study**
   - See [Kursk Conversion](../examples/Kursk_Conversion.md) for detailed analysis
   - 95.3% accuracy achieved!

5. **Read advanced guides**
   - [CLI Tools Reference](../reference/CLI_Tools.md) - All available commands
   - [Troubleshooting Guide](../guides/Troubleshooting.md) - Comprehensive solutions
   - [Multi-Game Support](../architecture/Multi_Era_Support.md) - Add other Battlefield games

---

**Last Updated:** October 2025
**Tutorial Version:** 1.0
**Tested With:** BF1942 v1.6, Godot 4.3, Portal SDK 2025

**Need Help?**
- 💬 [GitHub Discussions](https://github.com/yourusername/PortalSDK/discussions)
- 🐛 [Report Issues](https://github.com/yourusername/PortalSDK/issues)

**See Also:**
- [CLI Tools Reference](../reference/CLI_Tools.md) - Complete command documentation
- [Kursk Case Study](../examples/Kursk_Conversion.md) - Detailed conversion analysis
- [Troubleshooting Guide](../guides/Troubleshooting.md) - Common issues and solutions
- [Main README](../../README.md) - Project overview
