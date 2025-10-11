# Phase 1: BF1942 Data Analysis

## Overview

This document summarizes Phase 1 findings about BF1942 file structures and extraction requirements.

## RFA Extraction Research

### What Are RFA Files?

- **Format**: Refractor Archive (.rfa)
- **Purpose**: Compressed archives containing game assets
- **Compression**: LZO algorithm
- **Contents**: Maps, textures, configurations, models, sounds

### Kursk Map Files Located

```
bf1942_source/Mods/bf1942/Archives/bf1942/levels/
├── Kursk.rfa        (10.4 MB) - Main map archive
├── Kursk_000.rfa    (68 KB)   - Patch 1
└── Kursk_003.rfa    (14 KB)   - Patch 2
```

### RFA Extraction Tools

**Option 1: Windows Tools (Recommended for Phase 1)**
- **BGA** (Battlefield Game Archive) - https://github.com/yann-papouin/bga
  - Full-featured GUI tool
  - File preview, extraction, repacking
  - Written in Pascal/Delphi
- **WinRFA** - Classic simple extractor
- **rfaUnpack.exe** - Command-line tool

**Option 2: Python Implementation (Deferred to Phase 3)**
- Requires reverse engineering RFA binary format
- Dependencies: `python-lzo` for decompression
- No existing complete Python parser found (as of 2025-10-10)

### Recommendation

**For Phase 1:** Use BGA on Windows gaming PC to extract Kursk RFAs

1. Download BGA from GitHub
2. Extract all three Kursk RFA files
3. Copy extracted folder to Mac: `bf1942_source/extracted/Kursk/`

Alternative: Install Wine on Mac and run BGA.exe

## .CON File Format Analysis

### What Are .CON Files?

- **Format**: Text-based configuration/script files
- **Purpose**: Define game objects, properties, and logic
- **Syntax**: Custom scripting language used by Refractor Engine

### .CON File Syntax Patterns

Based on analysis of `bf1942_source/Mods/bf1942/Settings/`:

```con
rem *** Comments start with 'rem' ***

game.addModPath Mods/BF1942/
game.setCustomGameVersion 1.6

ControlMap.create LandSeaPlayerInputControlMap
ControlMap.addKeyToTriggerMapping c_PIUse IDFKeyboard IDKey_E c_CMPushAndHold
```

**Key Patterns:**
1. `rem` - Comments
2. `game.*` - Global game settings
3. `ControlMap.*` - Input mappings
4. Object property syntax: `Object.property value`
5. Method call syntax: `Object.method param1 param2 ...`

### Expected Map .CON Files (After RFA Extraction)

Based on BF1942 modding documentation, map RFAs typically contain:

```
Kursk/
├── Info/
│   ├── Kursk.desc                  # Map description
│   └── Kursk.ai                    # AI pathfinding data
├── Gameplay/
│   ├── GameplayObjects.con         # Main object placement file
│   │   - Contains all static objects
│   │   - Defines positions, rotations, types
│   │   - Example syntax:
│   │       Object.create <type>
│   │       Object.absolutePosition <x>/<y>/<z>
│   │       Object.rotation <pitch>/<yaw>/<roll>
│   ├── ControlPoints.con          # Conquest objectives
│   ├── SpawnPoints.con            # Player/vehicle spawns
│   └── init.con                   # Map initialization
├── Heightdata/
│   ├── HeightMap.raw              # Terrain heightmap (binary)
│   └── HeightMap.con              # Heightmap metadata
├── Textures/
│   └── *.dds                      # Terrain textures
└── StaticObjects/
    └── *.sm                        # Static mesh files
```

## Data We Need to Extract

### 1. Object Placements

**From:** `GameplayObjects.con` or similar

**Extract:**
- Object type (e.g., `Bunker_German_01`, `Tank_Spawner`)
- Position (x, y, z coordinates)
- Rotation (pitch, yaw, roll)
- Team ownership (Axis/Allies/Neutral)
- Object properties (health, flags, etc.)

**Example .con syntax (expected):**
```con
rem *** Bunker at north base ***
Object.create Bunker_German_01
Object.absolutePosition 152.5/12.3/387.9
Object.rotation 0/45/0
Object.team 1
Object.setHealth 1000
```

### 2. Spawn Points

**From:** `SpawnPoints.con`

**Extract:**
- Spawn type (infantry, vehicle, aircraft)
- Position and orientation
- Team assignment
- Spawn group/ID

**BF6 Requirement:** Minimum 4 spawn points per team

### 3. Control Points (Capture Points)

**From:** `ControlPoints.con`

**Extract:**
- Control point ID and name
- Position
- Radius
- Initial owner
- Connected spawn points

**Note:** BF6 Portal has `CapturePoint` objects - direct mapping possible

### 4. Terrain Data

**From:** `HeightMap.raw`

**Challenge:** Cannot import custom terrain into BF6
**Approach:**
- Analyze heightmap to understand terrain features
- Document key elevations, valleys, hills
- Select closest matching BF6 terrain
- Plan manual sculpting in Godot

### 5. Combat Boundaries

**From:** May be in `GameplayObjects.con` or separate config

**Extract:**
- Out-of-bounds area definition
- Playable area polygon

**BF6 Requirement:** `CombatArea` with `PolygonVolume`

## BF1942 → BF6 Data Mapping

### Coordinate System

**BF1942 (Refractor):**
- Right-handed, Y-up
- Units: meters
- Format: `x/y/z` (slash-separated)

**BF6 (Godot):**
- Right-handed, Y-up
- Units: meters
- Format: Transform3D matrix

**Conversion:** Straightforward, same coordinate system

### Object Types

**BF1942 Object Examples:**
- `Bunker_German_01`
- `Hangar_German_01`
- `House_Rural_01`
- `Tree_Oak_01`
- `Tank_Spawner_Axis`

**BF6 Equivalent:**
Must map to available BF6 assets in `FbExportData/asset_types.json`

Example mapping (to be built in Phase 3):
- `Bunker_German_01` → `Military_Bunker_02` (or closest match)
- `House_Rural_01` → `Building_House_Small_01`
- `Tree_Oak_01` → `Nature_Tree_Oak_Medium`

### Team System

**BF1942:**
- Team 1: Axis
- Team 2: Allies

**BF6:**
- Team 1: Team 1
- Team 2: Team 2

Direct mapping possible.

## Next Steps (Remaining Phase 1 Tasks)

1. ✅ Research RFA extraction tools
2. ⏳ **EXTRACT KURSK RFAs**
   - Use BGA on Windows gaming PC
   - Extract to: `bf1942_source/extracted/Kursk/`
3. ⏳ Analyze extracted .con files
   - Parse object placement syntax
   - Identify all object types used
   - Document coordinate ranges
4. ⏳ Document complete BF1942 data structures
   - Create .con file format specification
   - List all object types in Kursk
   - Map spawn points and control points

## Questions for User

1. **RFA Extraction Method:**
   - Use BGA on Windows gaming PC? (Recommended)
   - Install Wine on Mac to run BGA?
   - Wait for Python implementation in Phase 3?

2. **Scope:**
   - Start with Kursk only, or extract all maps?
   - Focus on gameplay objects first, defer terrain?

## References

- BGA Tool: https://github.com/yann-papouin/bga
- BF1942 Modding Docs: https://bfmods.com/mdt/
- RFA Overview: https://www.realtimerendering.com/erich/bf1942/mdt/tutorials/Overview/Overview.html

---

*Last Updated*: 2025-10-10
*Status*: Research complete, awaiting RFA extraction
