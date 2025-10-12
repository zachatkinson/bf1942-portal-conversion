# BF1942 Data Structures Reference

> Complete technical reference for Battlefield 1942 file formats, data structures, and coordinate systems

**Purpose:** Technical reference for BF1942 file formats (.con, .rfa, heightmaps), object spawner syntax, and coordinate systems for map conversion
**Last Updated:** October 2025
**Status:** Technical reference - accurate for BF1942 v1.6

---

## Overview

This document provides a technical reference for Battlefield 1942's data formats, focusing on structures relevant to map conversion.

## Table of Contents

- [File Formats](#file-formats)
  - [.RFA (Refractor Archive)](#rfa-refractor-archive)
  - [.CON (Configuration) Files](#con-configuration-files)
- [Map Structure](#map-structure-actual-after-rfa-extraction)
- [ObjectSpawns.con Format](#objectspawnscon-format)
  - [Common Spawner Types](#common-spawner-types)
  - [Position and Rotation](#position-and-rotation)
- [ControlPoints.con Format](#controlpointscon-format)
- [SoldierSpawns.con Format](#soldierspawnscon-format)
- [Heightmap.raw Format](#heightmapraw-format)
- [Team System](#team-system)
- [Object Properties Reference](#object-properties-reference)
- [Data Extraction Strategy](#data-extraction-strategy)
- [Conversion Challenges](#conversion-challenges)
- [References](#references)

---

## File Formats

### .RFA (Refractor Archive)

**Format**: Binary compressed archive
**Compression**: LZO algorithm
**Structure**:
```
Header (variable size)
├── Magic number: 0x00A6C23A (little-endian)
├── Version: 0x00000001
├── File table offset
└── File table size

File Table
├── Entry count
└── For each file:
    ├── Filename (null-terminated string)
    ├── File offset (4 bytes)
    ├── Uncompressed size (4 bytes)
    ├── Compressed size (4 bytes, 0 if uncompressed)
    └── Checksum/flags

File Data Blocks
└── LZO compressed or uncompressed data
```

**Extraction**: Use BGA, WinRFA, or implement custom parser

### .CON (Configuration) Files

**Format**: Plain text script
**Encoding**: ASCII
**Syntax**: Custom scripting language

**Keywords:**
- `rem` - Comment
- `run` - Execute another script
- `include` - Include another .con file

**Basic Structure:**
```con
rem *** Comments ***

Object.create <ObjectType>
Object.property value
Object.method param1 param2 param3

TemplateClass.create <ClassName>
TemplateClass.property value
```

**Common Patterns:**

1. **Object Creation:**
```con
Object.create BunkerGerman01
```

2. **Property Setting:**
```con
Object.absolutePosition 100.0/50.0/200.0
Object.rotation 0/45/0
Object.team 1
```

3. **Method Calls:**
```con
Object.setHealth 1000
Object.active 1
```

## Map Structure (Actual After RFA Extraction)

### Directory Layout

```
Kursk/
├── Init.con                         # Map initialization script
├── StaticObjects.con                # Static object placements (large file ~330KB)
├── Heightmap.raw                    # Terrain heightmap (binary, 128KB)
├── materialmap.raw                  # Terrain material/texture mapping
├── Conquest/                        # Conquest game mode
│   ├── ObjectSpawns.con            # PRIMARY: Vehicle spawner placements
│   ├── SoldierSpawns.con           # PRIMARY: Player spawn points
│   ├── ControlPoints.con           # Conquest capture points
│   ├── ObjectSpawnTemplates.con    # Vehicle spawner templates
│   ├── SoldierSpawnTemplates.con   # Spawn point templates
│   └── ControlPointTemplates.con   # Capture point templates
├── Init/
│   ├── Terrain.con                 # Heightmap configuration
│   └── SkyAndSun.con               # Lighting/atmosphere
├── Textures/                        # Terrain and detail textures
│   └── *.dds                       # DirectDraw Surface texture files
├── AI/                              # AI navigation data
│   └── *.ai                        # Pathfinding meshes
├── Sounds/                          # Ambient sound definitions
├── TDM/                             # Team Deathmatch mode (similar structure)
├── Ctf/                             # Capture the Flag mode (similar structure)
├── SinglePlayer/                    # Single player mission data
└── Pathfinding/                     # Bot pathfinding data
```

**Note:** This structure is from BF1942 v1.6. Earlier versions may differ slightly.

## ObjectSpawns.con Format

### Object Instance Syntax

**Syntax:**
```con
Object.create <SpawnerType>
Object.absolutePosition <x>/<y>/<z>
Object.rotation <pitch>/<yaw>/<roll>
Object.setOSId <ObjectSpawnerId>
Object.setTeam <team_id>
```

**Example (from actual Kursk ObjectSpawns.con):**
```con
rem*****************************************
rem ****          AXIS BASE1           *****
rem ****************************************

Object.create lighttankspawner
Object.absolutePosition 450.345/78.6349/249.093
Object.rotation 0/0.103998/1.52588e-005
Object.setOSId 1
Object.setTeam 1

Object.create heavytankspawner
Object.absolutePosition 388.567/78.7631/246.062
Object.rotation 0/-0.664717/-1.52588e-005
Object.setOSId 1
Object.setTeam 1
```

**Key Properties:**
- `Object.create` - Creates instance of a spawner type (e.g., `lighttankspawner`, `heavytankspawner`, `APCSpawner`)
- `Object.absolutePosition` - World position in meters (x/y/z)
- `Object.rotation` - Euler angles in degrees (pitch/yaw/roll)
- `Object.setOSId` - Object Spawn ID (links to control points)
- `Object.setTeam` - Team ownership (1=Axis, 2=Allies, unset=Neutral)

### Common Spawner Types

**Vehicle Spawners:**
- `lighttankspawner` - Light tank
- `heavytankspawner` - Heavy tank
- `APCSpawner` - Armored Personnel Carrier
- `ScoutCarSpawner` - Scout/reconnaissance vehicle
- `FighterSpawner` - Fighter aircraft
- `DiveBomberSpawner` - Bomber aircraft
- `AAGunSpawner` - Anti-aircraft gun
- `ArtillerySpawner` - Artillery piece

**Note:** Spawner types are lowercase in actual files (e.g., `lighttankspawner` not `LightTankSpawner`)

**Example (from Kursk):**
```con
Object.create lighttankspawner
Object.absolutePosition 450.345/78.6349/249.093
Object.rotation 0/0.103998/1.52588e-005
Object.setOSId 1
Object.setTeam 1
```

### Position and Rotation

**Position Format:** `x/y/z` (slash-separated floats)
- X: East-West axis
- Y: Vertical axis (up)
- Z: North-South axis
- Units: Meters

**Rotation Format:** `pitch/yaw/roll` (degrees)
- Pitch: X-axis rotation (up/down tilt)
- Yaw: Y-axis rotation (left/right spin)
- Roll: Z-axis rotation (barrel roll)

**Coordinate System:** Right-handed, Y-up

## ControlPoints.con Format

### Control Point Instance Syntax

**Syntax:**
```con
Object.create <ControlPointTemplateName>
Object.absolutePosition <x>/<y>/<z>
```

**Key Points:**
- Control points reference template names defined in `ControlPointTemplates.con`
- Templates define properties like radius, team, capture times
- Instances only specify position - all other properties come from template
- Template names indicate team/type (e.g., `AxisBase_1_Cpoint`, `openbase_lumbermill_Cpoint`)

**Example (from Kursk):**
```con
rem*****************************************
rem ****          AXIS BASE1           *****
rem ****************************************

Object.create AxisBase_1_Cpoint
Object.absolutePosition 437.315/77.8547/238.39

rem*****************************************
rem ****        ALLIES Base2           *****
rem ****************************************

Object.create AlliesBase_2_Cpoint
Object.absolutePosition 568.058/76.6406/849.956
```

## SoldierSpawns.con Format

### Infantry Spawn Point Syntax

**Syntax:**
```con
Object.create <SpawnPointTemplateName>
Object.absolutePosition <x>/<y>/<z>
Object.rotation <pitch>/<yaw>/<roll>
```

**Key Points:**
- Soldier spawn points reference template names defined in `SoldierSpawnTemplates.con`
- Template name indicates team and control point (e.g., `AxisSpawnPoint_1_1` = Axis team, control point 1, spawn #1)
- Rotation determines which direction player faces when spawning
- Multiple spawn points per control point for spread

**Example (from Kursk):**
```con
rem*****************************************
rem ****          AXIS BASE  1          *****
rem ****************************************

Object.create AxisSpawnPoint_1_1
Object.absolutePosition 464.978/77.9123/233.386
Object.rotation -67.3921/0/0.0342712

Object.create AxisSpawnPoint_1_2
Object.absolutePosition 406.791/78.1203/249.466
Object.rotation 165.672/0/1.52588e-005
```

## Heightmap.raw Format

**Format**: Binary raw data
**File**: `Heightmap.raw` (at map root level)
**Size**: Typically 128KB (256x256 heightmap at 2 bytes per pixel)

**Structure**:
- 16-bit unsigned integers (little-endian)
- Resolution: Typically 256x256 or 512x512
- Value range: 0-65535
- Maps to height in meters via yScale factor

**Metadata** (from Init/Terrain.con):
```con
GeometryTemplate.create patchTerrain terrainGeometry
GeometryTemplate.file bf1942\levels\<MapName>\Heightmap
GeometryTemplate.materialMap bf1942\levels\<MapName>\Materialmap
GeometryTemplate.worldSize <size>
GeometryTemplate.yScale <scale>
GeometryTemplate.waterLevel <height>
GeometryTemplate.seaFloorLevel <height>
```

**Key Parameters:**
- `worldSize` - Map size in meters (e.g., 1024 = 1024m x 1024m)
- `yScale` - Vertical scale multiplier (typically 0.5 - 1.0)
- `waterLevel` - Water plane elevation in meters
- Heightmap resolution interpolated to world size

**Conversion Formula:**
```
actual_height = (raw_value / 65535.0) * yScale * maxHeight
```

**Example (Kursk):**
```con
GeometryTemplate.worldSize 1024
GeometryTemplate.yScale 0.6
GeometryTemplate.waterLevel 72
```

## Team System

**Team IDs:**
- `0` - Neutral
- `1` - Axis (Germany, Japan, Italy)
- `2` - Allies (US, UK, Russia)

**Team-Specific Objects:**
- Many objects have team variants (e.g., `Bunker_German` vs `Bunker_British`)
- Spawn points and control points have team ownership

## Object Properties Reference

### Common Properties

| Property | Type | Description |
|----------|------|-------------|
| `absolutePosition` | Vector3 | World position (x/y/z) |
| `rotation` | Vector3 | Euler angles (pitch/yaw/roll) |
| `team` | Int | Team ownership (0/1/2) |
| `geometry` | String | Mesh filename |
| `active` | Bool | Whether object is active |
| `armour` | Float | Hit points/health |
| `networkableInfo` | String | Network sync settings |

### Spawn-Related Properties

| Property | Type | Description |
|----------|------|-------------|
| `spawnDelay` | Float | Seconds between spawns |
| `respawnTime` | Float | Vehicle respawn time |
| `timeUntilFirstSpawn` | Float | Initial spawn delay |
| `maxSpawns` | Int | Spawn limit (-1 = infinite) |
| `controlPointId` | Int | Linked control point |

### Control Point Properties

| Property | Type | Description |
|----------|------|-------------|
| `radius` | Float | Capture radius (meters) |
| `controlPointName` | String | Display name |
| `timeToTakeControl` | Float | Capture time (seconds) |
| `timeToLoseControl` | Float | Loss time (seconds) |

## Data Extraction Strategy

### Step 1: Extract RFA Archives

Use BGA or WinRFA tools to extract map RFA files to access .con files and heightmaps.

### Step 2: Parse .con Files

Parse the following key files for map conversion:
- `Conquest/ObjectSpawns.con` - Vehicle spawner positions
- `Conquest/SoldierSpawns.con` - Player spawn point positions
- `Conquest/ControlPoints.con` - Capture point positions
- `Init/Terrain.con` - Heightmap and terrain configuration
- `StaticObjects.con` - Static object placements (buildings, props)

### Step 3: Map to Portal Assets

Cross-reference BF1942 object types with available Portal assets using mapping databases.

### Step 4: Generate Portal Map

Transform coordinates, generate .tscn scene file, and test in Godot editor.

## Conversion Challenges

### 1. Terrain

- **Challenge:** Cannot import heightmaps into BF6
- **Solution:** Select closest BF6 terrain, manually sculpt

### 2. Objects

- **Challenge:** BF6 has limited asset library
- **Solution:** Map to closest equivalents, document substitutions

### 3. Gameplay Logic

- **Challenge:** BF1942 .con scripts have complex logic
- **Solution:** Extract only positional/structural data, recreate logic in BF6

### 4. Asset Restrictions

- **Challenge:** BF6 assets have `levelRestrictions`
- **Solution:** Use only unrestricted or compatible assets

---

**References:**
- [BF1942 Modding Tutorials](https://bfmods.com/mdt/) - Official modding documentation
- [RFA Format Overview](https://www.realtimerendering.com/erich/bf1942/mdt/tutorials/Overview/Overview.html) - File format specifications
- [BGA Tool](https://github.com/yann-papouin/bga) - Archive extraction utility

**Last Updated:** October 2025
**Status:** Technical reference - accurate for BF1942 v1.6

**See Also:**
- [Multi-Game Support Architecture](../architecture/Multi_Era_Support.md) - How BF1942 data is parsed by the engine
- [Toolset Plan](../architecture/BF_To_Portal_Toolset_Plan.md) - Complete conversion pipeline
- [Main README](../../README.md) - Project overview
