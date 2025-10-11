# BF1942 to BF6 Portal Map Conversion Project

## Project Overview

This project aims to recreate classic Battlefield 1942 maps in Battlefield 6 Portal by extracting positional and gameplay data from the original BF1942 files and mapping them to BF6's asset library.

**Key Concept**: We're not converting assets - we're extracting positions, dimensions, and gameplay logic, then replacing BF1942 objects with equivalent BF6 assets.

## Objectives

1. Analyze BF1942 source files to understand data structure
2. Extract positional/gameplay data from BF1942 maps
3. Build object mapping system (BF1942 assets → BF6 equivalents)
4. Create automated conversion pipeline (BF1942 → .tscn templates)
5. Test and refine with Kursk as proof-of-concept
6. Document everything in comprehensive claude.md

## Project Structure

```
PortalSDK/
├── GodotProject/          # BF6 Portal Godot project
│   ├── levels/            # Modern BF6 maps (.tscn)
│   ├── objects/           # BF6 asset library
│   └── static/            # Static terrain/assets
├── bf1942_source/         # Original BF1942 installation files
├── FbExportData/          # Exported .spatial.json files
├── code/                  # Conversion tools
│   └── gdconverter/       # Existing .tscn ↔ .json converter
├── mods/                  # Example Portal mods
└── python/                # Python runtime for tools
```

## Execution Plan

### Phase 1: Analysis & Setup
- [x] Explore `bf1942_source/` directory structure
- [ ] Identify map data locations and formats
- [ ] Research/implement RFA extraction tools
- [ ] Analyze BF1942 level file formats (.con, .sct, etc.)
- [ ] Document BF1942 data structures

### Phase 2: BF6 Asset Analysis
- [ ] Catalog all available BF6 Portal assets from `asset_types.json`
- [ ] Identify BF6 terrain options
- [ ] Document BF6 object categories and properties
- [ ] Create comprehensive BF6 asset reference

### Phase 3: Mapping & Conversion Tool
- [ ] Build BF1942 ↔ BF6 object mapping database
- [ ] Create RFA extraction utilities
- [ ] Write conversion script: BF1942 data → Godot .tscn format
- [ ] Handle coordinate system transformations
- [ ] Generate proper spawn points, HQs, combat areas

### Phase 4: Kursk Proof-of-Concept
- [ ] Extract Kursk map data
- [ ] Generate initial .tscn template
- [ ] Manual refinement in Godot editor
- [ ] Test export to .spatial.json
- [ ] Iterate and improve conversion accuracy

### Phase 5: Documentation
- [ ] Create `.claude/claude.md` with project architecture
- [ ] Document conversion workflow
- [ ] Create reusable templates for remaining maps
- [ ] Write best practices guide

## Technical Details

### BF6 Portal Map Format (.tscn)

Modern BF6 maps follow this structure:

1. **Scene Hierarchy**:
   - Root Node3D
   - TEAM_1_HQ & TEAM_2_HQ (HQ_PlayerSpawner instances)
   - SpawnPoints (4+ per team, linked to HQ)
   - CombatArea (with PolygonVolume defining playable boundaries)
   - Static layer (Terrain + Assets references)

2. **Required Gameplay Objects**:
   - `HQ_PlayerSpawner` with ObjId, team assignment, HQArea polygon
   - `SpawnPoint` entities with 3D transforms
   - `CombatArea` with CollisionPolygon3D (height + 2D point array)
   - Terrain/Assets references (map-specific .tscn files)

3. **Export Format** (.spatial.json):
   - `Portal_Dynamic` array (editable objects)
   - `Static` array (terrain + assets with transforms)
   - Transform matrices (right/up/front vectors + position)

### BF1942 Data Format

- **Container**: .rfa (Refractor Archive) - proprietary compressed archive
- **Map Files**: Typically .con (configuration/script files) and geometry data
- **To Extract**: Spawn points, control points, vehicle spawners, static object positions, combat boundaries

## Conversion Strategy

### Object Mapping Approach

For each BF1942 object:
1. Extract object type and position
2. Look up equivalent BF6 asset in mapping database
3. Apply scale/coordinate transformation
4. Generate Godot scene node with BF6 asset reference
5. Preserve gameplay properties (team, ObjId, etc.)

Example:
```
BF1942: "Bunker_German_01" at (123.4, 5.6, 789.0)
  ↓
BF6: "Military_Bunker_02" at transformed position
```

### Terrain Strategy

Since we can't import custom terrain:
1. Analyze BF1942 heightmap data (if accessible)
2. Select closest matching BF6 terrain template
3. Document manual adjustments needed
4. Use BF6's terrain sculpting tools in Godot

## Resources

- **Portal SDK README**: `/PortalSDK/README.html`
- **Unofficial Portal Docs**: https://github.com/NodotProject/Unofficial-BF6-Portal-SDK-Docs
- **BF6 Asset Types**: `/PortalSDK/FbExportData/asset_types.json`
- **Example Mods**: `/PortalSDK/mods/`
- **Conversion Tools**: `/PortalSDK/code/gdconverter/`

## Current Status

**Phase**: Initial Setup & Analysis
**Next Steps**:
1. Explore bf1942_source/ directory structure
2. Identify RFA extraction tools/methods
3. Begin cataloging BF1942 map formats

## Notes

- BF6 Portal is a curated sandbox - can only use EA-provided assets
- No custom geometry import - must use existing BF6 assets
- Focus on Kursk as simplest test case (open terrain, fewer buildings)
- This is a "recreation" not a "port" - think remaster, not direct conversion
