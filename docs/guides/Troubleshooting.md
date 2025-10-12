# Troubleshooting Guide

> Comprehensive solutions for common issues in BF1942 to Portal map conversion

**Purpose:** Complete troubleshooting reference for conversion issues, Godot errors, and Portal compatibility problems
**Last Updated:** October 2025
**Status:** Comprehensive Guide

---

## Table of Contents

- [Extraction Issues](#extraction-issues)
- [Conversion Failures](#conversion-failures)
- [Coordinate and Position Problems](#coordinate-and-position-problems)
- [Asset Mapping Issues](#asset-mapping-issues)
- [Godot Editor Problems](#godot-editor-problems)
- [Export Failures](#export-failures)
- [Portal Web Builder Issues](#portal-web-builder-issues)
- [In-Game Problems](#in-game-problems)
- [Performance Issues](#performance-issues)
- [Getting Help](#getting-help)

---

## Extraction Issues

### RFA Extraction Fails

**Error:** "Cannot open RFA file" or "Extraction failed"

**Possible Causes:**
1. Corrupted RFA archive
2. Wrong extraction tool version
3. File permissions issue

**Solutions:**

**Try different extraction tool:**
```bash
# Try BGA (recommended)
# Windows: Use BGA.exe GUI

# Try WinRFA
# Alternative Windows tool

# Try rfaUnpack
rfaUnpack.exe Kursk.rfa output/
```

**Verify RFA integrity:**
```bash
# Check file size (should be 5-50MB depending on map)
ls -lh bf1942_source/.../*.rfa

# Compare with known good checksums (if available)
md5sum Kursk.rfa
```

**Check permissions:**
```bash
# Ensure write access to output directory
chmod 755 bf1942_source/extracted/
```

---

### Extracted Files Missing

**Problem:** Extraction completes but missing .con files

**Expected files:**
```
Kursk/
├── Init.con
├── StaticObjects.con
├── Heightmap.raw
└── Conquest/
    ├── ObjectSpawns.con       ← Required
    ├── SoldierSpawns.con      ← Required
    ├── ControlPoints.con      ← Required
    └── *Templates.con
```

**Solutions:**

**Check extraction path:**
```bash
# Should extract to subdirectory, not root
BGA: Extract to "Kursk/"
Not: "." (current directory)
```

**Try full extraction:**
- Some tools have "Extract Selected" vs "Extract All"
- Use "Extract All" to ensure complete extraction

**Verify archive contents first:**
- Open RFA in BGA
- Browse file list before extracting
- Ensure .con files visible in archive

---

## Conversion Failures

### "Map directory not found"

**Error:**
```
FileNotFoundError: bf1942_source/extracted/.../Kursk/ not found
```

**Cause:** Incorrect path or map not extracted

**Solutions:**

**Verify extraction path:**
```bash
ls bf1942_source/extracted/Bf1942/Archives/bf1942/Levels/Kursk/

# Should show:
# Init.con
# StaticObjects.con
# Conquest/
```

**Specify custom path:**
```bash
python3 tools/portal_convert.py \
    --map Kursk \
    --base-terrain MP_Tungsten \
    --bf1942-root /custom/path/to/bf1942/Levels
```

**Check case sensitivity (Linux/macOS):**
```bash
# Wrong: kursk/
# Correct: Kursk/

# BF1942 uses mixed case
```

---

### "Mappings file not found"

**Error:**
```
FileNotFoundError: tools/asset_audit/bf1942_to_portal_mappings.json not found
```

**Cause:** Asset mapping database missing or not committed

**Solutions:**

**Generate mappings:**
```bash
# Create mapping database
python3 tools/create_asset_mappings.py --auto-suggest

# Verify creation
ls -lh tools/asset_audit/bf1942_to_portal_mappings.json
# Should be ~200KB with 733 mappings
```

**Download from repository:**
```bash
# If mappings not in git, download from releases
# Or copy from another working installation
```

---

### Conversion Crashes Mid-Process

**Error:** Python exception during conversion

**Common exceptions:**

**KeyError: 'asset_name':**
```python
KeyError: 'lighttankspawner'
```

**Cause:** Asset not in mapping database

**Solution:**
```bash
# Add missing asset to mappings.json
# Or update mapping database
python3 tools/create_asset_mappings.py --update
```

**MemoryError:**
```python
MemoryError: Unable to allocate array
```

**Cause:** Large map with many objects, insufficient RAM

**Solution:**
```bash
# Increase Python memory limit
python3 -X dev tools/portal_convert.py ...

# Or process in chunks (advanced)
```

---

## Coordinate and Position Problems

### Objects Floating in Air

**Symptom:** Objects 10-50m above terrain surface

**Causes:**
1. No heightmap provided
2. Wrong terrain height range
3. Incorrect coordinate transform

**Solutions:**

**Provide heightmap:**
```bash
python3 tools/portal_convert.py \
    --map Kursk \
    --base-terrain MP_Tungsten \
    --heightmap GodotProject/terrain/Kursk_heightmap.png \
    --min-height 73 \
    --max-height 217
```

**Re-adjust heights:**
```bash
python3 tools/portal_adjust_heights.py \
    --input GodotProject/levels/Kursk.tscn \
    --output GodotProject/levels/Kursk_fixed.tscn \
    --heightmap GodotProject/terrain/Tungsten_heightmap.png \
    --terrain-size 2048
```

**Debug in Godot:**
1. Open map in Godot
2. Select object
3. Inspector → Transform → Position
4. Note Y-coordinate
5. Compare to terrain Y at same X/Z

---

### Objects Underground

**Symptom:** Objects partially or fully below terrain

**Causes:**
1. Terrain height higher than expected
2. Negative height offset applied
3. Spawn points too low

**Solutions:**

**Increase height offset:**
```bash
python3 tools/portal_adjust_heights.py \
    --input GodotProject/levels/Kursk.tscn \
    --output GodotProject/levels/Kursk_raised.tscn \
    --heightmap GodotProject/terrain/Tungsten_heightmap.png \
    --height-offset 5.0  # Raise 5m
```

**Manual adjustment in Godot:**
1. Select all objects (Ctrl+A in 3D viewport)
2. Inspector → Transform → Position → Y
3. Add 5-10 to Y value
4. Save scene

---

### Objects Outside Combat Area

**Symptom:** Objects spawn outside playable boundary

**Causes:**
1. Incorrect coordinate offset
2. Wrong map center calculation
3. Scale mismatch

**Solutions:**

**Recalculate offset:**
```bash
# Debug: Print object positions
python3 tools/portal_parse.py --map Kursk --debug

# Find min/max X/Z
# Calculate center: (min+max)/2

# Apply correct offset
python3 tools/portal_convert.py \
    --map Kursk \
    --base-terrain MP_Tungsten \
    --debug  # Shows calculated offset
```

**Verify CombatArea:**
1. Open in Godot
2. Select CombatArea → CollisionPolygon3D
3. View → Top (for top-down view)
4. Check if all objects inside polygon
5. Adjust polygon points if needed

---

### Map Orientation Wrong

**Symptom:** Map rotated 90° or 180°

**Causes:**
1. N-S vs E-W terrain mismatch
2. Missing axis swap transformation
3. Wrong rotation applied

**Solutions:**

**Apply axis swap:**
```bash
# For N-S to E-W conversion
python3 tools/portal_convert.py \
    --map Kursk \
    --base-terrain MP_Tungsten \
    --transform swap_xz
```

**Manual rotation in Godot:**
1. Select root node (map name)
2. Transform → Rotation → Y
3. Try 90°, 180°, 270° until correct
4. Save scene

---

## Asset Mapping Issues

### Many "Asset not available" Warnings

**Warning:**
```
Warning: Asset 'PineTree' not available on MP_Tungsten, using fallback 'BirchTree'
```

**Cause:** Portal `levelRestrictions` - asset only works on specific maps

**This is NORMAL:** The mapper automatically uses fallbacks

**Verify fallbacks:**
```bash
# Check console output for fallback choices
# If many assets have no fallback, consider different base terrain
```

**Try different base terrain:**
```bash
# Some terrains have more compatible assets
python3 tools/portal_convert.py \
    --map Kursk \
    --base-terrain MP_Limestone  # Try different terrain
```

---

### Specific Asset Missing

**Error:**
```
AssetMappingError: No mapping found for 'CustomBF1942Asset'
```

**Cause:** Asset not in mapping database (custom mod asset, rare object)

**Solutions:**

**Add manual mapping:**
```json
// Edit tools/asset_audit/bf1942_to_portal_mappings.json
{
  "static_objects": {
    "CustomBF1942Asset": {
      "portal_equivalent": "GenericProp",
      "category": "prop",
      "notes": "Custom asset - using generic equivalent"
    }
  }
}
```

**Use generic fallback:**
```json
{
  "CustomBF1942Asset": {
    "portal_equivalent": "PLACEHOLDER",
    "category": "unknown"
  }
}
```

---

### Wrong Asset Type Mapped

**Problem:** Tank mapped to building, tree mapped to rock, etc.

**Cause:** Incorrect mapping in database

**Solution:**

**Update mapping:**
```json
// Edit bf1942_to_portal_mappings.json
{
  "vehicles": {
    "lighttankspawner": {
      "portal_equivalent": "VEH_Leopard",  // Correct tank
      "category": "vehicle",
      "confidence_score": 0.9
    }
  }
}
```

**Re-run conversion:**
```bash
python3 tools/portal_convert.py --map Kursk --base-terrain MP_Tungsten
```

---

## Godot Editor Problems

### Project Won't Import

**Error:** "Failed to open project" or "Invalid project.godot"

**Solutions:**

**Verify path:**
```bash
# Should select:
PortalSDK/GodotProject/project.godot

# Not:
PortalSDK/  # Too high
PortalSDK/GodotProject/levels/  # Too deep
```

**Check Godot version:**
```bash
# Required: Godot 4.3+
# Not compatible with: Godot 3.x

godot --version
# Should show: 4.3.x or higher
```

**Reimport project:**
1. Delete `.godot/` directory in GodotProject
2. Open project again
3. Wait for full reimport (2-5 minutes)

---

### BFPortal Tab Missing

**Symptom:** No BFPortal panel in editor

**Cause:** Plugin not enabled

**Solution:**
1. Project → Project Settings → Plugins
2. Find "BF Portal" plugin
3. Check "Enable"
4. Restart Godot

**If plugin not listed:**
```bash
# Verify plugin exists
ls GodotProject/addons/bf_portal/

# Should contain:
# - plugin.cfg
# - portal_tools/
```

---

### Scene Shows Red "!" Errors

**Symptom:** Red exclamation marks in scene tree

**Cause:** Missing asset references

**Solutions:**

**Check Portal SDK assets:**
```bash
# Verify Portal SDK files
ls GodotProject/raw/models/
# Should contain many .glb files (100-500MB each)
```

**Download missing assets:**
- Get full Portal SDK from EA/DICE
- Place .glb files in `GodotProject/raw/models/`
- Reload scene

**Check specific missing asset:**
1. Click node with "!"
2. Inspector → Script/Instance
3. Note missing file path
4. Verify file exists at path

---

### 3D Viewport Black/Empty

**Symptom:** Cannot see terrain or objects

**Solutions:**

**Reset camera:**
1. View → Top
2. View → Front
3. Try different angles

**Frame selection:**
1. Select terrain node
2. Press F key (frame selection)
3. Camera centers on object

**Check viewport settings:**
- Viewport → View Environment
- Ensure environment enabled
- Check Sky and lighting settings

---

## Export Failures

### "Export Current Level" Button Does Nothing

**Symptom:** Click button, nothing happens

**Causes:**
1. macOS/Linux (Windows-only button by default)
2. Export script error
3. Missing dependencies

**Solutions:**

**macOS/Linux - Use Manual Export:**
```bash
python3 code/gdconverter/src/gdconverter/export_tscn.py \
    GodotProject/levels/Kursk.tscn \
    FbExportData \
    FbExportData/levels
```

**Windows - Check Console:**
1. Bottom panel → Output
2. Look for error messages
3. Check for Python errors

**See:** [macOS Compatibility Guide](../setup/macOS_Compatibility_Patch.md) for details

---

### Empty or Truncated .spatial.json

**Symptom:** Export creates 0-byte file or incomplete JSON

**Causes:**
1. Missing required nodes
2. Invalid transform matrices
3. Export script crash

**Solutions:**

**Verify required nodes:**
```bash
# Must have:
# - TEAM_1_HQ
# - TEAM_2_HQ
# - CombatArea
# - Static

# Check in Godot scene tree
```

**Validate scene:**
```bash
python3 tools/portal_validate.py GodotProject/levels/Kursk.tscn
```

**Check export log:**
- Godot → Output panel
- Look for Python errors
- Note line number of failure

---

### Invalid JSON Error

**Error:** JSON validation fails

**Cause:** Malformed .spatial.json file

**Diagnosis:**
```bash
python3 -c "import json; json.load(open('FbExportData/levels/Kursk.spatial.json'))"

# Shows error location:
# json.decoder.JSONDecodeError: Expecting ',' delimiter: line 1234 column 5
```

**Solutions:**

**Re-export:**
```bash
# Delete bad export
rm FbExportData/levels/Kursk.spatial.json

# Re-export
# Godot → BFPortal → Export Current Level
```

**Manual JSON fix (advanced):**
- Open in text editor
- Find line number from error
- Fix syntax (missing comma, bracket, etc.)

---

## Portal Web Builder Issues

### Upload Fails

**Error:** "Invalid file format" or "Upload failed"

**Solutions:**

**Verify file format:**
```bash
# Must be .spatial.json
# Not .tscn or other format

file FbExportData/levels/Kursk.spatial.json
# Should show: JSON data
```

**Check file size:**
```bash
ls -lh FbExportData/levels/Kursk.spatial.json
# Should be: 500KB - 5MB
# If 0 bytes: Export failed
# If >10MB: May exceed Portal limit
```

**Validate JSON:**
```bash
python3 -c "import json; json.load(open('FbExportData/levels/Kursk.spatial.json')); print('✅ Valid JSON')"
```

---

### Map Loads but Looks Wrong

**Symptom:** Map loads in Portal builder but terrain/objects incorrect

**Common issues:**

**Missing terrain:**
- Check Static node has terrain reference
- Verify terrain type matches base terrain used

**Objects in wrong positions:**
- Coordinate transform issue
- Re-run conversion with correct offset

**Missing objects:**
- Asset mapping failures
- Check console output for skipped assets

---

## In-Game Problems

### Can't Spawn

**Symptom:** Cannot spawn when joining game

**Causes:**
1. Missing or invalid spawn points
2. Spawn points outside HQArea
3. Not enough spawn points (minimum 4)

**Solutions:**

**Verify spawn points:**
```bash
# Check Godot scene tree
TEAM_1_HQ
  ├── SpawnPoint_1_1  ← Minimum 4
  ├── SpawnPoint_1_2
  ├── SpawnPoint_1_3
  └── SpawnPoint_1_4

TEAM_2_HQ
  ├── SpawnPoint_2_1  ← Minimum 4
  ├── SpawnPoint_2_2
  ├── SpawnPoint_2_3
  └── SpawnPoint_2_4
```

**Check HQArea:**
1. HQ must have HQArea PolygonVolume
2. Spawn points must be inside HQArea
3. HQArea minimum 40m × 40m

---

### Vehicles Don't Spawn

**Symptom:** Vehicle spawners present but no vehicles appear

**Causes:**
1. Vehicle spawner not linked to control point
2. Wrong vehicle type for Portal
3. Spawner outside CombatArea

**Solutions:**

**Verify vehicle spawner:**
```bash
# Check scene tree
# Vehicle spawners should be children of control points
# Or at base locations
```

**Check vehicle type:**
- Portal may not have all BF1942 vehicle types
- Check asset mapping for vehicle substitutions

---

### Map Boundary Kills Players

**Symptom:** Players die when reaching map edge

**Cause:** CombatArea too small or incorrectly positioned

**Solution:**

**Adjust CombatArea:**
1. Godot → Select CombatArea → CollisionPolygon3D
2. Inspector → Points
3. Expand polygon to encompass all playable space
4. Save and re-export

---

## Performance Issues

### Godot Editor Slow

**Causes:**
1. Too many objects in scene
2. High-poly meshes
3. Insufficient RAM

**Solutions:**

**Reduce viewport quality:**
- Project → Project Settings → Rendering → Quality
- Lower shadow quality
- Reduce reflection quality

**Close unused panels:**
- Minimize Inspector when not needed
- Close FileSystem if not browsing

**Use LOD (Level of Detail):**
- For distant objects
- Reduces polygon count

---

### Conversion Takes Too Long

**Symptom:** Conversion runs for 10+ minutes

**Causes:**
1. Very large map (Stalingrad, Berlin)
2. Thousands of static objects
3. Complex asset mapping

**Solutions:**

**Profile conversion:**
```bash
python3 -m cProfile tools/portal_convert.py --map Kursk ...
# Shows which functions are slow
```

**Optimize asset mappings:**
- Pre-filter unused assets
- Cache mapping lookups

**Split large maps:**
- Convert in sections
- Combine in Godot

---

## Getting Help

### Before Asking for Help

**Gather this information:**

1. **Error messages** (full text)
2. **Command used** (exact command line)
3. **Map name** and BF1942 version
4. **Portal base terrain** used
5. **OS and versions:**
   ```bash
   python3 --version
   godot --version
   uname -a  # Linux/macOS
   ```
6. **File sizes:**
   ```bash
   ls -lh GodotProject/levels/YourMap.tscn
   ls -lh FbExportData/levels/YourMap.spatial.json
   ```

### Where to Get Help

- 💬 **GitHub Discussions:** https://github.com/yourusername/PortalSDK/discussions
- 🐛 **GitHub Issues:** https://github.com/yourusername/PortalSDK/issues
- 📖 **Documentation:** [docs/README.md](../README.md)

### Provide Debug Output

```bash
# Run with debug flag
python3 tools/portal_convert.py \
    --map Kursk \
    --base-terrain MP_Tungsten \
    --debug 2>&1 | tee conversion.log

# Share conversion.log when asking for help
```

---

**Last Updated:** October 2025
**Status:** Comprehensive Troubleshooting Guide
**Version:** 1.0

**See Also:**
- [Converting Your First Map](../tutorials/Converting_Your_First_Map.md) - Step-by-step tutorial
- [CLI Tools Reference](../reference/CLI_Tools.md) - Command documentation
- [Kursk Case Study](../examples/Kursk_Conversion.md) - Real-world example
- [Main README](../../README.md) - Project overview
