# Guide: Portal Map Testing

> Complete validation checklist for converted Battlefield maps in Portal

**Purpose:** Comprehensive testing procedures for validating converted maps from Godot to Portal
**Last Updated:** October 2025
**Difficulty:** Intermediate
**Time Required:** ~30-45 minutes per map
**Status:** Production Ready

---

## Table of Contents

- [Overview](#overview)
- [Pre-Test Setup](#pre-test-setup)
  - [Pull Latest Changes](#1-pull-latest-changes)
  - [Install Portal SDK Assets](#2-install-portal-sdk-assets)
  - [Open Project in Godot](#3-open-project-in-godot)
- [Phase 1: Godot Editor Verification](#phase-1-godot-editor-verification)
  - [Load the Map](#load-the-map)
  - [Visual Inspection Checklist](#visual-inspection-checklist)
- [Phase 2: Portal Export](#phase-2-portal-export)
  - [Export Process](#export-process)
  - [Export Verification](#export-verification)
- [Phase 3: Portal Web Builder](#phase-3-portal-web-builder)
  - [Upload to Portal](#upload-to-portal)
  - [Web Builder Checks](#web-builder-checks)
  - [Common Issues](#common-issues)
- [Phase 4: In-Game Testing](#phase-4-in-game-testing)
  - [Test Match Setup](#test-match-setup)
  - [Gameplay Checklist](#gameplay-checklist)
- [Phase 5: Post-Test Documentation](#phase-5-post-test-documentation)
  - [Record Results](#record-results)
  - [Report Issues](#report-issues)
- [Success Criteria](#success-criteria)
- [Troubleshooting](#troubleshooting)
- [Next Maps to Test](#next-maps-to-test)

---

## Overview

This guide provides step-by-step validation procedures for maps converted using the Portal SDK conversion pipeline. Use this checklist to ensure your converted maps meet quality standards before release.

**Testing Phases:**
1. Godot Editor - Visual inspection and asset verification
2. Portal Export - File generation and JSON validation
3. Portal Web Builder - Import and configuration testing
4. In-Game Testing - Gameplay validation
5. Post-Test Documentation - Results and issue tracking

> 💡 **Tip:** Complete each phase before moving to the next. Earlier phases catch issues faster than in-game testing.
> **Use:** Efficient debugging workflow

---

## Pre-Test Setup

### 1. Pull Latest Changes

```bash
cd PortalSDK
git pull origin master
```

### 2. Install Portal SDK Assets

The `.glb` model files are not in git (too large). You need to:

**Option A: Download Full Portal SDK**
- Download Portal SDK from EA/DICE
- Extract to `GodotProject/raw/models/`

**Option B: Copy from Development Machine**
- Copy `GodotProject/raw/models/*.glb` from development machine
- Via USB drive, network share, or cloud storage

**Option C: Verify Existing Installation**
```bash
ls GodotProject/raw/models/*.glb | wc -l
# Should show 50+ .glb files
```

> 📝 **Note:** Portal SDK .glb files are excluded from git due to 100MB file size limits. You must install them separately.
> **Use:** Understanding why assets aren't in repository

### 3. Open Project in Godot

- Launch Godot 4.5+ (Standard, not .NET)
- Open `PortalSDK/GodotProject/`
- Wait for initial import (may take a few minutes)

> ⚠️ **Warning:** Use Godot 4 Standard, NOT .NET version. The Portal SDK is not compatible with .NET.
> **Use:** Avoiding project compatibility issues

---

## Phase 1: Godot Editor Verification

### Load the Map

1. Open `GodotProject/levels/Kursk.tscn` (or your map)
2. Check for dependency errors (should be none if .glb files present)

### Visual Inspection Checklist

**Terrain & Layout:**
- [ ] Terrain mesh loads properly (MP_Tungsten or other base map)
- [ ] Combat area boundary is centered on map
- [ ] Assets are positioned on terrain (not floating/underground)

**Team HQs:**
- [ ] Team 1 HQ visible and positioned correctly
- [ ] Team 2 HQ visible and positioned correctly
- [ ] Each HQ has 4+ spawn points
- [ ] Spawn points are on ground level
- [ ] HQ areas (polygons) encompass spawn points

**Capture Points (if present):**
- [ ] Capture points positioned on terrain
- [ ] Capture point markers visible
- [ ] Capture areas defined

**Assets:**
- [ ] Trees loaded and positioned
- [ ] Buildings loaded and positioned
- [ ] Props loaded and positioned
- [ ] No major visual artifacts

**3D Viewport Navigation:**
- Use middle mouse to rotate view
- Use scroll wheel to zoom
- Use Shift + middle mouse to pan
- Check different angles of the map

> 💡 **Tip:** Use the 3D viewport top/front/side views to check for floating or underground objects quickly.
> **Use:** Efficient visual inspection workflow

---

## Phase 2: Portal Export

### Export Process

**Option A: All-in-One (Recommended)**
```bash
python3 tools/export_to_portal.py Kursk
```

**Option B: Modular (For Development)**
```bash
# Step 1: Export .tscn to .spatial.json
bash tools/export_map.sh Kursk

# Step 2: Create experience file
python3 tools/create_experience.py Kursk
```

> 📝 **Note:** The all-in-one tool is faster for final exports. Use modular workflow during development for quicker iteration.
> **Use:** Choosing the right workflow for your testing phase

### Export Verification

**Check .spatial.json:**
```bash
ls -lh FbExportData/levels/Kursk.spatial.json
# Should be 500KB - 5MB depending on asset count
```

**Check Experience File:**
```bash
ls -lh experiences/Kursk_Experience.json
# Should be 1-2MB (includes base64-encoded spatial data)
```

**JSON Validation:**
- [ ] .spatial.json is valid JSON (not truncated)
- [ ] Contains "Static" array
- [ ] Contains "Portal_Dynamic" array
- [ ] Terrain object present
- [ ] Multiple asset objects present
- [ ] Experience file has "mapRotation" array
- [ ] Experience file has "spatialAttachment" with base64 data

**Quick Validation Commands:**
```bash
# Validate spatial file
python3 -c "import json; data=open('FbExportData/levels/Kursk.spatial.json').read(); json.loads(data); print('✅ Valid spatial.json')"

# Validate experience file
python3 -c "import json; data=open('experiences/Kursk_Experience.json').read(); json.loads(data); print('✅ Valid experience.json')"
```

---

## Phase 3: Portal Web Builder

### Upload to Portal

1. Open BF6 Portal web builder (https://portal.battlefield.com)
2. Click **"IMPORT"** button (top-right menu)
3. Select `experiences/Kursk_Experience.json`
4. Wait for Portal to process import (10-30 seconds)
5. **IMPORTANT**: Go to **Map Rotation** panel
6. Click **"Add Map"** button
7. Select the **display name** for your base map:
   - For MP_Tungsten: Select **"Mirak Valley"**
   - For other maps: Check docs/Portal_Export_Guide.md "Available Base Maps" section
8. Portal combines the base terrain with your custom spatial data

> ⚠️ **Warning:** Portal requires you to manually add the base map in the UI even though the spatial data is embedded. This is a Portal requirement, not an error.
> **Use:** Understanding the two-step import process

### Web Builder Checks

- [ ] Import completed without errors
- [ ] Experience appears in your experiences list
- [ ] Map Rotation section shows "No maps chosen" initially (expected)
- [ ] After adding map: Shows base map display name (e.g., "Mirak Valley")
- [ ] Map preview loads in builder
- [ ] No "missing asset" warnings in console
- [ ] Can save experience

### Common Issues

**Issue: "No maps chosen" error persists after import**
- **Cause**: Forgot to manually add map in Portal Builder UI
- **Fix**: Go to Map Rotation panel → Add Map → Select display name (e.g., "Mirak Valley")

> 💡 **Tip:** The map ID in the experience JSON (e.g., "MP_Tungsten-ModBuilderCustom0") tells Portal which base terrain to use, but you still need to select it manually in the UI.
> **Use:** Understanding Portal's import workflow

**Issue: Don't know which map name to select**
- **Cause**: Map technical names (MP_Tungsten) differ from display names (Mirak Valley)
- **Fix**: Check docs/Portal_Export_Guide.md section "Available Base Maps" for the mapping table

**Issue: Import fails silently**
- **Cause**: Invalid experience JSON format
- **Fix**: Validate JSON with Phase 2 validation commands

**Issue: "Asset type not found"**
- **Cause**: Portal SDK version mismatch or invalid asset reference
- **Fix**: Verify Portal SDK version matches game version, regenerate experience file

**Issue: Terrain not centered**
- **Cause**: Coordinate offset issue in conversion
- **Fix**: Check terrain positioning in Godot editor, verify conversion used correct base terrain

**Issue: Assets floating/underground**
- **Cause**: Height sampling issue during conversion
- **Fix**: Verify terrain mesh bounds and Y-axis positioning in Godot

---

## Phase 4: In-Game Testing

### Test Match Setup

**For Custom Mode (Recommended for Testing):**
1. In Portal Builder, your experience uses custom mode by default
2. Save and publish your experience
3. Launch Battlefield 6
4. Go to Portal → Find your experience
5. Create local match (supports testing without publishing)

> 📝 **Note:** All maps in this project use custom mode (ModBuilder_GameMode: 0) to enable local testing and full control over Portal Builder settings.
> **Use:** Understanding why custom mode is used

**Basic Game Setup:**
- Game mode: Conquest
- Teams: 2 teams
- Players: 16-64 (depending on testing needs)
- Time limit: 10-20 minutes

### Gameplay Checklist

**Spawning:**
- [ ] Can spawn at Team 1 HQ
- [ ] Can spawn at Team 2 HQ
- [ ] Spawn points work correctly (not stuck in objects)
- [ ] Spawn orientation is reasonable

**Movement:**
- [ ] Can walk on terrain
- [ ] No invisible walls
- [ ] Combat area boundary works (countdown when leaving)
- [ ] No falling through map

**Combat Area:**
- [ ] Boundary encompasses entire playable area
- [ ] Players warned when leaving boundary
- [ ] Players killed after countdown expires

**Asset Placement:**
- [ ] Trees are at ground level
- [ ] Buildings accessible (can enter if applicable)
- [ ] Props don't block movement
- [ ] No major clipping issues

**Capture Points (if applicable):**
- [ ] Can capture objectives
- [ ] Capture radius appropriate
- [ ] UI shows objective status

**Overall Feel:**
- [ ] Map layout matches original Battlefield map
- [ ] Scale feels appropriate
- [ ] Distances reasonable for combat
- [ ] Cover and sightlines preserved from original

---

## Phase 5: Post-Test Documentation

### Record Results

Create `test_results/MapName_YYYY-MM-DD.md`:

```markdown
# [MapName] Test Results - [Date]

## Summary
- **Status**: Pass/Fail/Partial
- **Conversion Accuracy**: X%
- **Major Issues**: None / List issues

## Detailed Results

### Godot Editor
- [x] Loaded successfully
- [ ] Issue: [description]

### Portal Export
- [x] Exported successfully
- [ ] Issue: [description]

### In-Game
- [x] Spawns work
- [x] Movement works
- [ ] Issue: [description]

## Screenshots
- [Attach screenshots if possible]

## Next Steps
- [ ] Fix issue X
- [ ] Adjust asset Y
- [ ] Test feature Z
```

### Report Issues

If you find bugs or issues:
1. Take screenshots (F12 in Godot, game screenshot key)
2. Note exact reproduction steps
3. Check console output for errors
4. Document in test results file
5. Create GitHub issue if it's a conversion pipeline bug

---

## Success Criteria

**Minimum Viable Product:**
- ✅ Map loads in Godot
- ✅ Exports to Portal
- ✅ Players can spawn
- ✅ Players can move around map
- ✅ Combat area boundary works

**Full Success:**
- ✅ All MVP criteria
- ✅ Assets placed correctly (95%+ accuracy)
- ✅ Terrain height matches original
- ✅ Capture points work (if applicable)
- ✅ Map feels like original Battlefield map

---

## Troubleshooting

### Godot Won't Open Map
**Symptoms**: Dependency errors, missing resources
**Solution**: Install Portal SDK .glb files to `GodotProject/raw/models/`

### Export Button Missing
**Symptoms**: No BFPortal panel in Godot
**Solution**:
1. Check `addons/` folder present
2. Enable plugin: Project → Project Settings → Plugins → BFPortal

### Export Creates Empty File
**Symptoms**: Very small .spatial.json (< 10KB)
**Solution**: Check Godot console for errors, verify map has required nodes (HQs, spawns)

### Map Doesn't Load in Portal
**Symptoms**: Portal web builder shows errors
**Solution**:
1. Validate JSON syntax with Phase 2 commands
2. Check asset type names match Portal catalog
3. Verify terrain type exists

### Players Spawn Underground
**Symptoms**: Spawns below terrain
**Solution**:
1. Check terrain height grid is loaded in Godot
2. Verify spawn point Y coordinates in .tscn
3. Re-export with height validation enabled

---

## Next Maps to Test

After Kursk validation:
1. **Wake Island** - Tests island terrain with water boundaries
2. **El Alamein** - Tests desert terrain and vehicle-heavy gameplay
3. **Stalingrad** - Tests urban environment and dense building placement

Each map tests different conversion features:
- **Kursk**: Flat terrain, rural assets, open combat
- **Wake**: Water boundaries, beach terrain, island layout
- **El Alamein**: Desert environment, vehicle spawners, long sightlines
- **Stalingrad**: Dense urban, building interiors, vertical gameplay

---

**Next Steps:**
1. [Portal Export Guide](./docs/Portal_Export_Guide.md) - Complete export workflow and options
2. [Troubleshooting Guide](./docs/guides/Troubleshooting.md) - Additional problem-solving
3. [Maps Registry](./maps_registry.json) - View all planned maps

**Last Updated:** October 2025
**Status:** Production Ready
**See Also:**
- [Portal Export Guide](./docs/Portal_Export_Guide.md) - Export workflow
- [macOS Setup](./docs/setup/macOS_Compatibility_Patch.md) - macOS-specific procedures
- [Project README](./README.md) - Project overview
