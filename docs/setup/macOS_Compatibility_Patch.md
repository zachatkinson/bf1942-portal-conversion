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

Use the provided export helper script:

```bash
bash tools/export_map.sh Kursk
```

**That's it!** Your map is now at `FbExportData/levels/Kursk.spatial.json` and ready to import into the Battlefield Portal web builder.

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

### Using the Export Script

The project includes `tools/export_map.sh` for easy exporting:

```bash
# Export any map by name
bash tools/export_map.sh <MapName>

# Examples:
bash tools/export_map.sh Kursk
bash tools/export_map.sh El_Alamein
bash tools/export_map.sh Iwo_Jima
```

### What the Script Does

1. **Validates Inputs**: Checks that `.tscn` file exists
2. **Runs Export**: Converts Godot scene to Portal JSON format
3. **Validates Output**: Confirms export succeeded
4. **Shows Results**: Displays file size and next steps

### Example Output

```
Exporting map: Kursk
  Input:  /Users/zach/Downloads/PortalSDK/GodotProject/levels/Kursk.tscn
  Output: /Users/zach/Downloads/PortalSDK/FbExportData/levels/Kursk.spatial.json

/Users/zach/Downloads/PortalSDK/FbExportData/levels/Kursk.spatial.json

✅ Export successful!
   File: /Users/zach/Downloads/PortalSDK/FbExportData/levels/Kursk.spatial.json
   Size: 912K

Next steps:
  1. Open Battlefield Portal web builder
  2. Import /Users/zach/Downloads/PortalSDK/FbExportData/levels/Kursk.spatial.json
  3. Test your map in-game!
```

### What Gets Exported

The `.spatial.json` file includes:
- Team HQs and spawn points
- Combat area boundaries
- Static terrain and assets
- Gameplay objects (capture points, triggers)
- All transform matrices for Portal

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

### Direct Python Export (Without Helper Script)

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

### Batch Export Multiple Maps

Create a simple loop:

```bash
for map in Kursk El_Alamein Iwo_Jima; do
  bash tools/export_map.sh "$map"
done
```

### Integration with CI/CD

The export script returns proper exit codes:
- `0` = Success
- `1` = Failure (validation error, file not found, etc.)

Example GitHub Actions workflow:

```yaml
- name: Export maps
  run: |
    pip3 install -e code/gdconverter
    bash tools/export_map.sh Kursk
```

---

## Summary

**Portal SDK is fully functional on macOS!**

### Complete Workflow

1. **Install dependencies once**: `pip3 install -e code/gdconverter`
2. **Edit maps in Godot**: Ignore the setup error, open `.tscn` files
3. **Export for Portal**: `bash tools/export_map.sh <MapName>`
4. **Import to Portal**: Use the `.spatial.json` file in the web builder

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
bash tools/export_map.sh Kursk

# Done! Upload Kursk.spatial.json to Portal
```

---

**Last Updated:** October 12, 2025
**Status:** ✅ Production-ready macOS workflow
**Platform:** macOS 12+ (tested on macOS Sequoia 15.0)

**See Also:**
- [Godot Setup Guide](./Godot_Setup_Guide.md) - Godot 4 installation
- [Project README](../../README.md) - Portal SDK overview
