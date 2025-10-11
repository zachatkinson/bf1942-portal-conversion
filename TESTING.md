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
1. In Godot, with `Kursk.tscn` open
2. Look for **BFPortal** panel (usually on right side)
3. Verify export terrain shows "MP_Tungsten"
4. Click **"Export Current Level"** button
5. Wait for export to complete (10-30 seconds)

### Export Verification
Check `FbExportData/levels/Kursk.spatial.json`:
```bash
ls -lh FbExportData/levels/Kursk.spatial.json
# Should be 500KB - 5MB depending on asset count
```

**JSON Structure Check:**
- [ ] File is valid JSON (not truncated)
- [ ] Contains "Static" array
- [ ] Contains "Portal_Dynamic" array
- [ ] Terrain object present
- [ ] Multiple asset objects present

Quick check:
```bash
python3 -c "import json; data=open('FbExportData/levels/Kursk.spatial.json').read(); json.loads(data); print('Valid JSON')"
```

## Phase 3: Portal Web Builder

### Upload to Portal
1. Open BF6 Portal web builder
2. Navigate to map editor
3. Import/upload `Kursk.spatial.json`
4. Wait for Portal to process

### Web Builder Checks
- [ ] Map loads without errors
- [ ] Terrain visible in preview
- [ ] Assets visible in preview
- [ ] No "missing asset" warnings
- [ ] Combat area boundary visible

### Common Issues

**Issue**: "Asset type not found"
- **Cause**: Portal SDK version mismatch
- **Fix**: Verify Portal SDK version matches game version

**Issue**: Terrain not centered
- **Cause**: Coordinate offset issue
- **Fix**: Check `portal_convert.py` terrain center calculation

**Issue**: Assets floating/underground
- **Cause**: Height sampling issue
- **Fix**: Verify terrain mesh bounds and height grid

## Phase 4: In-Game Testing

### Test Match Setup
1. Create custom game mode in Portal
2. Select Kursk map
3. Set up basic rules:
   - Conquest mode
   - 2 teams
   - 10-20 minute timer

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
