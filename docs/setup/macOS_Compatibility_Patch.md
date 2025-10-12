# macOS Compatibility for BF6 Portal SDK

**Purpose:** Full-featured Portal SDK workflow for macOS - map editing and export
**Last Updated:** October 12, 2025
**Status:** ✅ Production Ready
**Difficulty:** Easy
**Time Required:** ~5 minutes

---

## Table of Contents

- [Overview](#overview)
- [What Works on macOS](#what-works-on-macos)
- [Quick Start](#quick-start)
- [Map Editing Workflow](#map-editing-workflow)
- [Map Export Workflow](#map-export-workflow)
- [Understanding the Setup Error](#understanding-the-setup-error)
- [Troubleshooting](#troubleshooting)

---

## Overview

**Portal SDK works completely on macOS!** 🎉

This project includes a streamlined macOS workflow that provides:
- ✅ Full map editing in Godot 4
- ✅ One-command map export to Portal format
- ✅ No Windows machine required
- ✅ Professional tooling with error handling

The Windows-only "Setup" button error can be safely ignored - it only affects an unnecessary GUI feature.

---

## What Works on macOS

### ✅ Map Editing (Godot Editor)
- Open and edit `.tscn` map files
- Full 3D viewport navigation
- Object placement and manipulation
- Inspector panel and scene tree
- Save changes
- All Portal SDK assets available

### ✅ Map Export (Command Line)
- Convert `.tscn` → `.spatial.json` for Portal
- Create complete Portal experience files
- Validate asset references
- Professional error handling
- Single-command operation

### ❌ Windows-Only Features (Not Needed)
- **"Setup" GUI Button**: Creates Python virtual environment on Windows
  - **Impact**: None - Python already configured in this project
- **"Export Level" GUI Button**: Convenience wrapper for export script
  - **Impact**: None - we have a better command-line tool

---

## Quick Start

### 1. Install Dependencies

The `gdconverter` package must be installed once:

```bash
cd code/gdconverter
pip3 install -e .
```

This installs the Godot scene parser (`lark`) and export tools.

### 2. Export Your Map

**Option A: All-in-One Export (Recommended)**

```bash
python3 tools/export_to_portal.py Kursk
```

This creates a complete Portal experience file ready to import.

**Option B: Modular Workflow (For Development)**

```bash
# Step 1: Export .tscn to .spatial.json
bash tools/export_map.sh Kursk

# Step 2: Create experience file
python3 tools/create_experience.py Kursk
```

**That's it!** Your experience file is at `experiences/Kursk_Experience.json` and ready to import into the Battlefield Portal web builder.

---

## Map Editing Workflow

### Opening a Map

1. **Launch Godot 4.5+**
   ```bash
   # Open the Portal SDK project
   open GodotProject/project.godot
   ```

2. **Ignore the Setup Error**

   You'll see this message:
   ```
   ERROR: Setup has not been implemented for your platform: macOS
   ```

   **Click "OK" and continue** - this only affects a Windows-specific GUI button. All editing features work perfectly.

3. **Open Your Map**

   In Godot's FileSystem panel:
   - Navigate to `res://levels/`
   - Double-click `Kursk.tscn` (or your map)
   - Scene loads normally ✅

### Editing Your Map

All Godot editing features work normally:
- **3D Viewport**: Navigate, select objects, move/rotate/scale
- **Scene Tree**: View node hierarchy
- **Inspector**: Edit node properties
- **Portal Tools Panel**: View asset library
- **Save**: `Ctrl+S` / `Cmd+S` saves changes

---

## Map Export Workflow

### Export Options

**Option 1: All-in-One (Recommended for Final Export)**

```bash
python3 tools/export_to_portal.py Kursk
```

Creates both `.spatial.json` and complete experience file in one command.

**Option 2: Modular (Recommended for Development)**

```bash
# Step 1: Export .tscn to .spatial.json
bash tools/export_map.sh Kursk

# Step 2: Create experience file
python3 tools/create_experience.py Kursk
```

Use this during development for faster iteration - you can re-export the map without recreating the experience file each time.

### What the Tools Do

**export_map.sh:**
1. Validates `.tscn` file exists
2. Converts Godot scene to Portal JSON format
3. Outputs `.spatial.json` to `FbExportData/levels/`
4. Shows file size and confirmation

**create_experience.py / export_to_portal.py:**
1. Reads `.spatial.json` file (or exports it first)
2. Base64 encodes the spatial data
3. Wraps in complete Portal experience structure
4. Outputs experience file to `experiences/` directory

### Example Output

```
============================================================
Step 1: Exporting Kursk.tscn to .spatial.json
============================================================

Exporting Kursk to .spatial.json...
✅ Created FbExportData/levels/Kursk.spatial.json

============================================================
Step 2: Creating Portal experience file
============================================================

✅ Created experiences/Kursk_Experience.json
   Base map: MP_Tungsten
   Game mode: Conquest
   Max players: 64
   Spatial data: 912,345 bytes
   Experience file: 1,216,460 bytes

============================================================
✅ SUCCESS! Ready to import to Portal
============================================================

Import file: experiences/Kursk_Experience.json

Next steps:
1. Go to portal.battlefield.com
2. Click the 'IMPORT' button
3. Select: experiences/Kursk_Experience.json
4. Add map in Portal Builder UI (select "Mirak Valley" for MP_Tungsten)
5. Your map will appear in Map Rotation!
```

### What Gets Exported

**The `.spatial.json` file includes:**
- Team HQs and spawn points
- Combat area boundaries
- Static terrain and assets
- Gameplay objects (capture points, triggers)
- All transform matrices for Portal

**The experience file includes:**
- Complete game mode configuration (Conquest verified mode)
- Base64-encoded spatial data
- Player count and team settings
- Map rotation settings
- Ready-to-import format

---

## Understanding the Setup Error

### Why the Error Appears

The Portal SDK plugin checks for a Windows-only Python virtual environment setup. On macOS/Linux, this check fails and shows an error dialog.

### Why You Can Ignore It

The "Setup" button only performs these Windows-specific tasks:
1. Creates a Python virtual environment at `python/`
2. Runs `pip install` using Windows executables
3. Uses PowerShell commands

**None of these are needed on macOS** because:
- Python is already configured in this project
- The `gdconverter` package is installed via pip
- Export works via direct Python script execution

### What Actually Matters

The critical functionality that **does work** on macOS:
- ✅ Object library generation (runs before the error)
- ✅ Godot scene editing (not affected by setup)
- ✅ Python export script (cross-platform)

---

## Troubleshooting

### Error: "No module named 'gdconverter'"

**Solution**: Install the gdconverter package:

```bash
cd code/gdconverter
pip3 install -e .
```

This installs the package in editable mode, making it available to Python.

### Error: "Map file not found"

**Solution**: The export script expects map names without `.tscn` extension:

```bash
# Correct:
bash tools/export_map.sh Kursk

# Incorrect:
bash tools/export_map.sh Kursk.tscn
```

If your map has a different name, check available maps:

```bash
ls GodotProject/levels/*.tscn
```

### Error: "Export script not found"

**Solution**: Run the export script from the project root directory:

```bash
cd /Users/zach/Downloads/PortalSDK
bash tools/export_map.sh Kursk
```

### Godot Shows "Missing Dependencies"

**Solution**: Ensure Godot 4.5+ is installed. The Portal SDK requires Godot 4 Standard (not .NET).

Download from: https://godotengine.org/download/macos/

### Export Produces Empty or Invalid JSON

**Solution**: Check the console output for validation errors. Common issues:
- Missing required nodes (HQs, spawn points)
- Invalid asset references
- Malformed transform matrices

Review the `.tscn` file structure in Godot to ensure all required components exist.

---

## Advanced Usage

### Custom Export Settings

Customize your experience file with options:

```bash
# Custom base map and player count
python3 tools/create_experience.py Kursk \
  --base-map MP_Outskirts \
  --max-players 32 \
  --description "Epic tank battle on the Eastern Front"

# Or with all-in-one tool
python3 tools/export_to_portal.py Kursk \
  --base-map MP_Outskirts \
  --max-players 64 \
  --game-mode Conquest
```

**Available base maps:** MP_Tungsten (Mirak Valley), MP_Outskirts (New Sobek City), MP_Battery (Iberian Offensive), MP_Firestorm (Operation Firestorm), and more. See `FbExportData/map_names.json` for complete list with display names.

### Batch Export Multiple Maps

Create a simple loop:

```bash
for map in Kursk El_Alamein Iwo_Jima; do
  python3 tools/export_to_portal.py "$map"
done
```

### Direct Python Export (Low-Level)

If you prefer running the export script directly:

```bash
python3 code/gdconverter/src/gdconverter/export_tscn.py \
  GodotProject/levels/Kursk.tscn \
  FbExportData \
  FbExportData/levels
```

**Arguments:**
1. Path to `.tscn` file
2. Path to `FbExportData` directory (asset catalog)
3. Output directory for `.spatial.json`

### Integration with CI/CD

The export script returns proper exit codes:
- `0` = Success
- `1` = Failure (validation error, file not found, etc.)

Example GitHub Actions workflow:

```yaml
- name: Export maps
  run: |
    pip3 install -e code/gdconverter
    python3 tools/export_to_portal.py Kursk
```

---

## Summary

**Portal SDK is fully functional on macOS!**

### Complete Workflow

1. **Install dependencies once**: `pip3 install -e code/gdconverter`
2. **Edit maps in Godot**: Ignore the setup error, open `.tscn` files
3. **Export for Portal**: `python3 tools/export_to_portal.py <MapName>`
4. **Import to Portal**: Upload the experience JSON file
5. **Add map in UI**: Select base map (e.g., "Mirak Valley" for MP_Tungsten)
6. **Test in-game**: Publish and play!

### No Windows Machine Needed

This project provides a complete, professional macOS workflow:
- ✅ Cross-platform Python export script
- ✅ Robust error handling and validation
- ✅ Clear feedback and next steps
- ✅ Easy to maintain and extend

### Getting Started

```bash
# One-time setup
cd code/gdconverter
pip3 install -e .

# Export your map
python3 tools/export_to_portal.py Kursk

# Done! Upload Kursk_Experience.json to Portal
# Then add "Mirak Valley" in Portal Builder UI
```

---

**Last Updated:** October 12, 2025
**Status:** ✅ Production-ready macOS workflow
**Platform:** macOS 12+ (tested on macOS Sequoia 15.0)

**See Also:**
- [Portal Export Guide](../Portal_Export_Guide.md) - Complete export workflow and options
- [Godot Setup Guide](./Godot_Setup_Guide.md) - Godot 4 installation
- [Project README](../../README.md) - Portal SDK overview
