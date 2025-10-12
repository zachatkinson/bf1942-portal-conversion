# Testing Guide - Portal Map Conversion

This guide provides a checklist for testing converted Battlefield maps in Portal.

## Pre-Test Setup (PC)

### 1. Pull Latest Changes
```bash
cd PortalSDK
git pull origin master
```

### 2. Install Portal SDK Assets
The `.glb` model files are not in git (too large). You need to:

**Option A**: Download full Portal SDK
- Download Portal SDK from EA/DICE
- Extract to `GodotProject/raw/models/`

**Option B**: Copy from Mac
- Copy `GodotProject/raw/models/*.glb` from Mac to PC
- Via USB drive, network share, or cloud storage

**Option C**: Verify existing installation
```bash
ls GodotProject/raw/models/*.glb | wc -l
# Should show 50+ .glb files
```

### 3. Open Project in Godot
- Launch Godot 4.5 (Standard, not .NET)
- Open `PortalSDK/GodotProject/`
- Wait for initial import (may take a few minutes)

## Phase 1: Godot Editor Verification

### Load the Map
1. Open `GodotProject/levels/Kursk.tscn`
2. Check for dependency errors (should be none if .glb files present)

### Visual Inspection Checklist

**Terrain & Layout:**
- [ ] Terrain mesh loads properly (MP_Tungsten)
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

### Export Verification

**Check .spatial.json:**
```bash
ls -lh FbExportData/levels/Kursk.spatial.json
# Should be 500KB - 5MB depending on asset count
```

**Check experience file:**
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

Quick validation:
```bash
# Validate spatial file
python3 -c "import json; data=open('FbExportData/levels/Kursk.spatial.json').read(); json.loads(data); print('✅ Valid spatial.json')"

# Validate experience file
python3 -c "import json; data=open('experiences/Kursk_Experience.json').read(); json.loads(data); print('✅ Valid experience.json')"
```

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
   - For other maps: Check `FbExportData/map_names.json` for display names
8. Portal combines the base terrain with your custom spatial data

### Web Builder Checks
- [ ] Import completed without errors
- [ ] Experience appears in your experiences list
- [ ] Map Rotation section shows "No maps chosen" initially (expected)
- [ ] After adding map: Shows base map name (e.g., "Mirak Valley")
- [ ] Map preview loads in builder
- [ ] No "missing asset" warnings in console
- [ ] Can save experience

### Common Issues

**Issue**: "No maps chosen" error persists after import
- **Cause**: Forgot to manually add map in Portal Builder UI
- **Fix**: Go to Map Rotation panel → Add Map → Select display name (e.g., "Mirak Valley")

**Issue**: Don't know which map name to select
- **Cause**: Map technical names (MP_Tungsten) differ from display names (Mirak Valley)
- **Fix**: Check `FbExportData/map_names.json` for the mapping

**Issue**: Import fails silently
- **Cause**: Invalid experience JSON format
- **Fix**: Validate JSON with `python3 -c "import json; json.load(open('experiences/Kursk_Experience.json'))"`

**Issue**: "Asset type not found"
- **Cause**: Portal SDK version mismatch or invalid asset reference
- **Fix**: Verify Portal SDK version matches game version

**Issue**: Terrain not centered
- **Cause**: Coordinate offset issue
- **Fix**: Check terrain positioning in Godot editor

**Issue**: Assets floating/underground
- **Cause**: Height sampling issue
- **Fix**: Verify terrain mesh bounds and Y-axis positioning

## Phase 4: In-Game Testing

### Test Match Setup

**For Custom Mode (Local Testing):**
1. In Portal Builder, ensure your experience uses custom mode
2. Save and publish your experience
3. Launch Battlefield 6
4. Go to Portal → Find your experience
5. Create local match or invite friends

**For Published Experiences:**
1. In Portal Builder, configure game settings
2. Click **"Save and Publish"**
3. Launch Battlefield 6
4. Go to Portal → "My Experiences"
5. Select Kursk experience
6. Start match (public or private)

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
- [ ] Map layout matches BF1942 Kursk
- [ ] Scale feels appropriate
- [ ] Distances reasonable for combat
- [ ] Cover and sightlines preserved from original

## Phase 5: Post-Test Documentation

### Record Results

Create `test_results/Kursk_YYYY-MM-DD.md`:

```markdown
# Kursk Test Results - [Date]

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
- ✅ Map feels like BF1942 Kursk

## Troubleshooting

### Godot Won't Open Map
**Symptoms**: Dependency errors, missing resources
**Solution**: Install Portal SDK .glb files

### Export Button Missing
**Symptoms**: No BFPortal panel in Godot
**Solution**:
1. Check `addons/` folder present
2. Enable plugin: Project → Project Settings → Plugins → BFPortal

### Export Creates Empty File
**Symptoms**: Very small .spatial.json (< 10KB)
**Solution**: Check Godot console for errors

### Map Doesn't Load in Portal
**Symptoms**: Portal web builder shows errors
**Solution**:
1. Validate JSON syntax
2. Check asset type names match Portal catalog
3. Verify terrain type exists

### Players Spawn Underground
**Symptoms**: Spawns below terrain
**Solution**:
1. Check terrain height grid is loaded
2. Verify spawn point Y coordinates
3. Re-run conversion with height validation

## Next Maps to Test

After Kursk validation:
1. Wake Island (island terrain with water)
2. El Alamein (desert terrain)
3. Stalingrad (urban environment)

Each map tests different conversion features:
- **Kursk**: Flat terrain, rural assets
- **Wake**: Water boundaries, beach terrain
- **El Alamein**: Desert, vehicle-heavy
- **Stalingrad**: Dense urban, buildings

---

**Good luck with testing!** Report any issues you find so we can improve the conversion pipeline.
