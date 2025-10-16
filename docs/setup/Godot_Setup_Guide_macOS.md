# Godot 4 Setup Guide for macOS - BF6 Portal SDK

> Complete guide for installing Godot 4 on macOS and opening Portal SDK projects for map development

**Platform:** macOS only
**Last Updated:** October 2025
**Difficulty:** Beginner
**Time Required:** ~15 minutes

---

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
  - [Option 1: Direct Download (Recommended)](#option-1-direct-download-recommended)
  - [Option 2: Homebrew](#option-2-homebrew)
  - [Option 3: Steam](#option-3-steam)
- [Opening the Portal SDK Project](#opening-the-portal-sdk-project)
- [Verifying Installation](#verifying-installation)
- [Working with Maps](#working-with-maps)
  - [Opening a Map](#opening-a-map)
  - [Viewing the Scene Tree](#viewing-the-scene-tree)
  - [3D Viewport Navigation](#3d-viewport-navigation)
- [Exporting Maps](#exporting-maps)
- [Troubleshooting](#troubleshooting)
  - [Project Won't Import](#project-wont-import)
  - [BFPortal Tab Missing](#bfportal-tab-missing)
  - [Missing Assets / Red Meshes](#missing-assets--red-meshes)
  - [Map Scene Shows Errors](#map-scene-shows-errors)
  - [Terrain Not Visible](#terrain-not-visible)
  - [Export Fails](#export-fails)
  - [macOS Gatekeeper Issues](#macos-gatekeeper-issues)
- [Performance Tips](#performance-tips)
- [Next Steps](#next-steps)
- [Additional Resources](#additional-resources)

---

## Requirements

**Godot Version:** 4.3 or later (Standard edition)

⚠️ **IMPORTANT:** Download the **STANDARD** version, **NOT** .NET/Mono

The Portal SDK uses GDScript only (not C#). You do not need the .NET version.

**macOS Version:** macOS 10.13 (High Sierra) or later recommended

---

## Installation

### Option 1: Direct Download (Recommended)

1. Visit https://godotengine.org/download/macos/
2. Download **Godot 4.3+ Standard** (NOT .NET version)
   - Choose the **macOS Universal** build for best compatibility
3. Open the `.dmg` file
4. Drag `Godot.app` to your Applications folder
5. **First launch:** Right-click → Open (to bypass Gatekeeper)
   - You only need to do this once
   - After first launch, you can open normally from Applications

**Gatekeeper Bypass:**
```bash
# Alternative: Remove quarantine flag to bypass Gatekeeper
xattr -d com.apple.quarantine /Applications/Godot.app
```

### Option 2: Homebrew

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Godot
brew install godot

# Launch from terminal
godot
```

### Option 3: Steam

1. Open Steam
2. Search for "Godot Engine"
3. Install (free download)
4. Launch from Steam Library

---

## Opening the Portal SDK Project

1. Launch Godot 4
2. Click **"Import"** in the Project Manager
3. Navigate to your repository: `PortalSDK/GodotProject/`
4. Select `project.godot`
5. Click **"Import & Edit"**

**First-time import:** Wait for asset import to complete (2-5 minutes depending on hardware)

**macOS Performance Tip:** If import is slow, check System Settings → Privacy & Security → Files and Folders to ensure Godot has full access.

---

## Verifying Installation

After opening the project, verify:

- [ ] Project opens without errors
- [ ] **BFPortal** tab appears in the editor (right panel or top menu)
- [ ] You can navigate the `FileSystem` panel
- [ ] `levels/` folder is visible with `.tscn` files

---

## Working with Maps

### Opening a Map

1. In the FileSystem panel, navigate to `res://levels/`
2. Double-click any `.tscn` file (e.g., `Kursk.tscn`)
3. The scene opens in the 3D viewport

### Viewing the Scene Tree

Every Portal map has this structure:
- **Root Node** (map name)
  - **TEAM_1_HQ** (with spawn points as children)
  - **TEAM_2_HQ** (with spawn points as children)
  - **CombatArea** (playable boundary)
  - **Static** (terrain and assets)
  - (Optional) VehicleSpawners, CapturePoints, etc.

### 3D Viewport Navigation

**macOS Shortcuts:**
- **Two-finger drag (trackpad)**: Rotate view
- **Pinch (trackpad)**: Zoom in/out
- **Shift + Two-finger drag**: Pan view
- **F Key**: Frame selection (focus on selected node)

**With Mouse:**
- **Middle Mouse Button**: Rotate view
- **Scroll Wheel**: Zoom in/out
- **Shift + Middle Mouse**: Pan view

---

## Exporting Maps

### Export to Portal Format

1. Open your map `.tscn` file in Godot
2. Click the **BFPortal** tab (usually in right panel)
3. Click **"Export Current Level"** button
4. Choose output location (default: `FbExportData/levels/`)
5. The `.spatial.json` file is created

### Testing the Export

Check that the `.spatial.json` file:
- Is 500KB - 5MB in size (depending on asset count)
- Contains valid JSON (no truncation)
- Has both `"Static"` and `"Portal_Dynamic"` arrays

Quick validation:
```bash
python3 -c "import json; json.load(open('FbExportData/levels/YourMap.spatial.json')); print('✅ Valid JSON')"
```

---

## Troubleshooting

### Project Won't Import

**Symptom:** "Failed to open project" error

**Solution:**
- Ensure you selected `GodotProject/project.godot` (not the root `PortalSDK/` folder)
- Check Godot version is 4.3+ (not Godot 3.x)
- Verify you have read/write permissions for the directory

### BFPortal Tab Missing

**Symptom:** No BFPortal panel in editor

**Solution:**
1. Go to **Project → Project Settings → Plugins**
2. Enable "**BF Portal**" plugin
3. Restart Godot if needed

### Missing Assets / Red Meshes

**Symptom:** Pink/red materials or missing meshes

**Cause:** Portal SDK `.glb` files not present

**Solution:**
- The large `.glb` model files are not in git (100-500MB each)
- Download the full Portal SDK from EA/DICE
- Place `.glb` files in `GodotProject/raw/models/`

See the main [README.md](../../README.md) for more information.

### Map Scene Shows Errors

**Symptom:** "Failed to load resource" errors when opening `.tscn`

**Solution:**
- Check that Portal SDK assets exist:
  - `res://objects/Gameplay/Common/HQ_PlayerSpawner.tscn`
  - `res://objects/entities/SpawnPoint.tscn`
  - `res://objects/Gameplay/Conquest/CapturePoint.tscn`
  - `res://static/[TERRAIN_NAME]_Terrain.tscn`

### Terrain Not Visible

**Symptom:** Gray/empty viewport when opening map

**Solution:**
- Wait for scene to fully load (large terrains take time)
- Check 3D viewport camera position
- Select terrain node and press **F** to frame it
- Try **View → Top** or **View → Front** to reset camera

### Export Fails

**Symptom:** "Export failed" or empty `.spatial.json`

**Solution:**
- Check Godot console (bottom panel) for error messages
- Ensure map has required components (HQs, CombatArea, Static)
- Verify BFPortal plugin is enabled
- Try closing and reopening the scene

### macOS Gatekeeper Issues

**Symptom:** "Godot.app can't be opened because it is from an unidentified developer"

**Solution 1 - Right-click Open:**
1. Locate `Godot.app` in Applications
2. Right-click (or Ctrl-click) → Open
3. Click "Open" in the dialog
4. macOS will remember this for future launches

**Solution 2 - Remove Quarantine:**
```bash
xattr -d com.apple.quarantine /Applications/Godot.app
```

**Solution 3 - System Settings:**
1. Open System Settings → Privacy & Security
2. Scroll to "Security" section
3. Click "Open Anyway" next to Godot warning
4. Launch Godot again

---

## Performance Tips

### Large Maps

- Use **LOD (Level of Detail)** for distant objects
- Reduce viewport quality during editing: **Project → Project Settings → Rendering → Quality**
- Close unnecessary editor panels

### Asset Import

- Initial import is slow (one-time operation)
- Subsequent opens are fast
- If import seems stuck, check Output panel for progress

### macOS-Specific Optimization

- **Metal Rendering:** Godot 4 uses Metal on macOS for best performance
- **Retina Displays:** Lower editor scale if UI feels slow (Editor → Editor Settings → Interface → Editor Scale)
- **Background Apps:** Close heavy apps during editing for better performance

---

## Next Steps

After setting up Godot:

1. **Test a map** - Open an existing `.tscn` file to verify setup
2. **Export** - Try exporting to `.spatial.json` format
3. **Portal Web Builder** - Upload the `.spatial.json` to BF6 Portal builder
4. **In-Game Testing** - Play your map in BF6 Portal

For detailed testing procedures, see [Testing_Guide.md](../../Testing_Guide.md)

---

## Additional Resources

- **Godot Documentation**: https://docs.godotengine.org/en/stable/
- **Portal SDK Docs**: [README.html](../../README.html)
- **Conversion Tools**: [docs/architecture/](../architecture/)
- **macOS Compatibility**: [macOS_Compatibility_Patch.md](./macOS_Compatibility_Patch.md)

---

**Last Updated:** October 2025
**Platform:** macOS only
**Godot Version:** 4.3+
**SDK Compatibility:** BF6 Portal SDK (2025)

**See Also:**
- [Windows Setup Guide](./Godot_Setup_Guide_Windows.md) - Windows installation
- [Testing_Guide.md](../../Testing_Guide.md) - Testing procedures
- [Main README](../../README.md) - Project overview
