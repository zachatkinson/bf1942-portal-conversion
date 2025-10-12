# Guide: Portal Export

> Complete workflow for exporting BF1942 maps to Battlefield 6 Portal

**Purpose:** Complete workflow for exporting BF1942 maps to Battlefield 6 Portal
**Last Updated:** October 2025
**Difficulty:** Intermediate
**Time Required:** ~15 minutes

---

## Table of Contents

- [Quick Reference](#quick-reference)
  - [Option 1: All-in-One Export](#option-1-all-in-one-export-fastest)
  - [Option 2: Modular Workflow](#option-2-modular-workflow-better-for-iteration)
  - [Option 3: Custom Settings](#option-3-custom-settings)
- [Complete Workflow](#complete-workflow)
  - [1. Edit Map in Godot](#1-edit-map-in-godot)
  - [2. Export to Portal Format](#2-export-to-portal-format)
  - [3. Import to Portal Builder](#3-import-to-portal-builder)
  - [4. Publish and Test](#4-publish-and-test)
- [Tool Reference](#tool-reference)
  - [export_map.sh](#exportmapsh)
  - [create_experience.py](#create_experiencepy)
  - [export_to_portal.py](#export_to_portalpy)
- [Available Base Maps](#available-base-maps)
- [Understanding the Experience Format](#understanding-the-experience-format)
  - [What is a Portal Experience?](#what-is-a-portal-experience)
  - [File Structure](#file-structure)
  - [Key Requirements](#key-requirements)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
  - [During Development](#during-development)
  - [For Release](#for-release)
  - [Version Control](#version-control)
- [Examples](#examples)
  - [Example 1: Quick Export](#example-1-quick-export)
  - [Example 2: Custom Settings](#example-2-custom-settings)
  - [Example 3: Multiple Maps](#example-3-multiple-maps)
  - [Example 4: Testing Workflow](#example-4-testing-workflow)
- [Advanced Topics](#advanced-topics)
  - [Custom Base Map Selection](#custom-base-map-selection)
  - [Multiple Game Modes](#multiple-game-modes)
- [Quick Command Reference](#quick-command-reference)

---

## Quick Reference

### Option 1: All-in-One Export (Fastest)

```bash
# Export .tscn and create Portal experience in one command
python3 tools/export_to_portal.py Kursk
```

### Option 2: Modular Workflow (Better for Iteration)

> 💡 **Tip:** Use this workflow during development for faster iteration - you can re-export just the map without recreating the experience file each time.
> **Use:** Recommended for active map development and testing

```bash
# Step 1: Export .tscn to .spatial.json
bash tools/export_map.sh Kursk

# Step 2: Create Portal experience file
python3 tools/create_experience.py Kursk
```

### Option 3: Custom Settings

```bash
# Export with custom base map and player count
python3 tools/create_experience.py Kursk \
  --base-map MP_Outskirts \
  --max-players 64 \
  --game-mode Conquest \
  --description "Epic WWII tank battle"
```

---

## Complete Workflow

### 1. Edit Map in Godot

```bash
# Open Godot project
open GodotProject/project.godot

# Edit levels/Kursk.tscn
# - Adjust spawn points
# - Place vehicles
# - Set combat area
# - Save changes
```

### 2. Export to Portal Format

```bash
# Option A: All-in-one
python3 tools/export_to_portal.py Kursk

# Option B: Modular (recommended during development)
bash tools/export_map.sh Kursk
python3 tools/create_experience.py Kursk
```

**Output:** `Kursk_Experience.json` (ready to import)

### 3. Import to Portal Builder

1. Go to https://portal.battlefield.com
2. Click **"IMPORT"** button (top-right menu)
3. Select `Kursk_Experience.json`
4. Wait for import to complete
5. Map appears in **Map Rotation** panel!

### 4. Publish and Test

1. Configure game mode settings (optional)
2. Click **"Save and Publish"**
3. Launch Battlefield 6
4. Find your experience in Portal
5. Play test!

---

## Tool Reference

### `export_map.sh`

**Purpose:** Export Godot .tscn to Portal .spatial.json

**Single Responsibility:** Map conversion only (no experience wrapping)

```bash
bash tools/export_map.sh <map_name>
```

**Output:**
- `FbExportData/levels/<map_name>.spatial.json`

**Use When:**
- Testing map edits quickly
- You want to manually create experience later
- Building custom workflow

---

### `create_experience.py`

**Purpose:** Wrap .spatial.json in complete Portal experience format

**Single Responsibility:** Experience file creation only

```bash
python3 tools/create_experience.py <map_name> [options]
```

**Options:**
- `--base-map <MP_Name>` - Base map for terrain (default: MP_Tungsten)
- `--max-players {16|32|64}` - Players per team (default: 32)
- `--game-mode <mode>` - Conquest, Rush, TeamDeathmatch, Breakthrough
- `--description "<text>"` - Custom experience description

**Output:**
- `<map_name>_Experience.json` (ready to import)

**Use When:**
- You already have .spatial.json
- You want to customize game settings
- Repackaging same map with different settings

---

### `export_to_portal.py`

**Purpose:** All-in-one export from .tscn to Portal experience

**Combines:** `export_map.sh` + `create_experience.py`

```bash
python3 tools/export_to_portal.py <map_name> [options]
```

**Same options as create_experience.py**

**Output:**
- `FbExportData/levels/<map_name>.spatial.json`
- `<map_name>_Experience.json`

**Use When:**
- Quick export from Godot to Portal
- First time export
- You don't need the intermediate .spatial.json

---

## Available Base Maps

Choose a base map with terrain similar to your BF1942 map:

| Technical Name | Display Name | Theater | Terrain Type |
|----------------|--------------|---------|--------------|
| **MP_Tungsten** | **Mirak Valley** | Tajikistan | Mountains, valleys (default for Kursk) |
| MP_Capstone | Liberation Peak | Tajikistan | High mountains |
| MP_Outskirts | New Sobek City | Cairo | Desert, urban outskirts |
| MP_Abbasid | Siege of Cairo | Cairo | Urban cityscape |
| MP_Battery | Iberian Offensive | Gibraltar | Rocky coastal terrain |
| MP_Limestone | Saint's Quarter | Gibraltar | Coastal cliffs |
| MP_Aftermath | Empire State | Brooklyn | Urban ruins |
| MP_Dumbo | Manhattan Bridge | Brooklyn | Dense urban |
| MP_Firestorm | Operation Firestorm | Turkmenistan | Desert wasteland |

> 📝 **Note:** When adding maps in Portal Builder, use the **Display Name** (e.g., "Mirak Valley"). The technical name is used in the experience JSON file.
> **Use:** Understanding the difference between technical and display names

**Recommendation for BF1942 maps:**
- **Kursk** → Mirak Valley (MP_Tungsten) - open terrain
- **El Alamein** → Operation Firestorm (MP_Firestorm) - desert
- **Wake Island** → Saint's Quarter (MP_Limestone) - island/coastal
- **Berlin** → Empire State (MP_Aftermath) - urban ruins
- **Stalingrad** → Empire State (MP_Aftermath) - urban warfare

---

## Understanding the Experience Format

### What is a Portal Experience?

A Portal "experience" is a complete game mode package including:
- **Game mode** (Conquest, Rush, etc.)
- **Map rotation** (one or more maps)
- **Game settings** (player counts, rules)
- **Custom spatial data** (your BF1942 map layout)

> 📝 **Note:** The maps in this project use **Custom Mode** (`ModBuilder_GameMode: 0`) to enable local testing and full control over Portal Builder settings. Custom mode supports Conquest gameplay while allowing you to test unpublished experiences and modify all game settings in the Portal UI.
> **Use:** Understanding the experience format and custom mode benefits

### How Portal Processes Custom Spatial Data

Portal uses a **server-side processing workflow** for custom map data:

**Import (What You Upload):**
```json
{
  "mapRotation": [{
    "id": "MP_Tungsten-ModBuilderCustom0",
    "spatialAttachment": {
      "filename": "Kursk.spatial.json",
      "attachmentData": {
        "original": "<base64_encoded_spatial_data>"
      }
    }
  }]
}
```

**Processing:**
1. Portal receives your experience file with embedded spatial data
2. Server extracts and validates the base64 spatial data
3. Stores spatial data in Portal's database
4. Links it to the map reference `MP_Tungsten-ModBuilderCustom0`
5. Converts map ID to `MP_Tungsten-Conquest0` in UI

**Export (What Portal Saves):**
```json
{
  "mapRotation": [{
    "id": "MP_Tungsten-Conquest0"
  }]
}
```

> 💡 **Tip:** Portal removes the `spatialAttachment` after processing. This is normal - your custom map data is stored server-side and linked to the map reference.
> **Use:** Understanding why exported experiences look different from imported ones

**Key Takeaways:**
- ✅ Import requires `spatialAttachment` with base64 data
- ✅ Portal processes and stores spatial data server-side
- ✅ Export only shows simplified map reference
- ✅ `-ModBuilderCustom0` suffix indicates custom spatial data
- ✅ Portal converts to `-Conquest0` after processing

### File Structure

```json
{
  "mutators": { /* game settings */ },
  "name": "Kursk - BF1942 Classic",
  "gameMode": "Conquest",
  "mapRotation": [
    {
      "id": "MP_Tungsten-ModBuilderCustom0",  // CRITICAL: Must end with -ModBuilderCustom0
      "spatialAttachment": {
        "filename": "Kursk.spatial.json",
        "attachmentData": {
          "original": "base64_encoded_spatial_data..."
        }
      }
    }
  ]
}
```

### Key Requirements

> ⚠️ **Warning:** Map ID format is critical - Portal will silently fail if incorrect!
> **Use:** Critical requirement for all Portal experience files

**Map ID Format:**
- ✅ `MP_Tungsten-ModBuilderCustom0` (correct)
- ❌ `MP_Tungsten-Kursk` (wrong - Portal won't recognize it)
- ❌ `MP_Tungsten` (wrong - missing suffix)

**Spatial Data:**
- Must be base64 encoded
- Must be in `attachmentData.original` field
- Our tools handle this automatically

> ✅ **Success:** When using our tools, all format requirements are handled automatically. You don't need to worry about these technical details.
> **Use:** Verification that automated tools handle complex requirements

---

## Troubleshooting

> 💡 **Tip:** Most import issues are caused by incorrect file format. Always use our export tools to ensure compliance with Portal SDK standards.
> **Use:** Troubleshooting import and format errors

### "No maps chosen" Error

**Cause:** Portal requires you to manually add the base map in the UI, even with custom spatial data

**Solution:**
1. After importing your experience
2. Go to **Map Rotation** section in Portal Builder
3. Click **"Add Map"**
4. Select the display name (e.g., "Mirak Valley" for MP_Tungsten)
5. Portal will combine the base terrain with your custom spatial data

> 📝 **Note:** The experience JSON defines the custom spatial attachment, but Portal still requires you to select which base map(s) to use in the UI.
> **Use:** Understanding the two-step process for custom maps

### "Map not appearing in rotation after import"

**Cause:** Incorrect map ID format

**Solution:** Re-export with our tools (they use correct format)

```bash
python3 tools/create_experience.py Kursk
```

### "Import succeeded but map rotation empty"

**Cause:** Map ID doesn't end with `-ModBuilderCustom0`

**Fix:** Use the provided tools, they handle this correctly

### "Spatial data not loading"

**Cause:** Spatial data not base64 encoded

**Fix:** Our tools encode automatically, don't manually create files

### "Experience file too large"

**Explanation:** Normal! Experience files can be 1-2MB due to embedded spatial data

The base64 encoding increases size by ~33%, but this is expected and works fine.

---

## Best Practices

### During Development

Use **modular workflow** for faster iteration:

```bash
# Edit in Godot → Save
bash tools/export_map.sh Kursk

# Test in Portal → Find issues
# Edit in Godot → Save
bash tools/export_map.sh Kursk

# When happy with map:
python3 tools/create_experience.py Kursk
```

### For Release

Use **all-in-one** for final export:

```bash
python3 tools/export_to_portal.py Kursk \
  --max-players 64 \
  --description "Authentic recreation of the iconic Kursk tank battle"
```

### Version Control

**Commit to git:**
- ✅ `.tscn` files (source)
- ✅ `.spatial.json` files (intermediate)
- ❌ `*_Experience.json` (generated, too large)

Add to `.gitignore`:
```
*_Experience.json
```

---

## Examples

### Example 1: Quick Export

```bash
# Just export with defaults
python3 tools/export_to_portal.py Kursk
```

### Example 2: Custom Settings

```bash
# Large-scale 128 player battle
python3 tools/create_experience.py Kursk \
  --max-players 64 \
  --game-mode Conquest \
  --base-map MP_Tungsten \
  --description "Massive 128-player recreation of the Battle of Kursk"
```

### Example 3: Multiple Maps

```bash
# Export multiple maps
for map in Kursk El_Alamein Wake_Island; do
  python3 tools/export_to_portal.py "$map"
done
```

### Example 4: Testing Workflow

```bash
# 1. Make changes in Godot
# 2. Quick export
bash tools/export_map.sh Kursk

# 3. Create test experience
python3 tools/create_experience.py Kursk --max-players 16

# 4. Import to Portal for testing
# 5. Repeat until happy

# 6. Final export with full settings
python3 tools/create_experience.py Kursk \
  --max-players 64 \
  --description "Final version"
```

---

## Advanced Topics

### Custom Base Map Selection

If your BF1942 map has unique terrain, choose the closest BF6 base map:

```bash
# For desert maps
python3 tools/create_experience.py El_Alamein --base-map MP_FireStorm

# For urban maps
python3 tools/create_experience.py Berlin --base-map MP_Aftermath

# For island maps
python3 tools/create_experience.py Wake_Island --base-map MP_Limestone
```

### Multiple Game Modes

Create different experiences for the same map:

```bash
# Conquest version (large scale)
python3 tools/create_experience.py Kursk \
  --max-players 64 \
  --game-mode Conquest

# Rush version (focused combat)
python3 tools/create_experience.py Kursk \
  --max-players 32 \
  --game-mode Rush

# Output: Kursk_Experience.json (overwrites each time)
# Rename manually if you want to keep both
```

---

## Quick Command Reference

```bash
# View all options
python3 tools/export_to_portal.py --help
python3 tools/create_experience.py --help

# Export with defaults
bash tools/export_map.sh Kursk
python3 tools/create_experience.py Kursk

# Export with custom settings
python3 tools/export_to_portal.py Kursk \
  --base-map MP_Outskirts \
  --max-players 64 \
  --game-mode Conquest

# List available maps
ls GodotProject/levels/*.tscn

# List exported spatial files
ls FbExportData/levels/*.spatial.json
```

---

**Next Steps:**
1. [macOS Compatibility Patch](./setup/macOS_Compatibility_Patch.md) - Setup Portal SDK on macOS
2. [Project Architecture](../.claude/CLAUDE.md) - Understanding the project structure

**Last Updated:** October 2025
