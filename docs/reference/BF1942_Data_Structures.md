# BF1942 Data Structures Reference

## Overview

This document provides a technical reference for Battlefield 1942's data formats, focusing on structures relevant to map conversion.

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

## Map Structure (Expected After RFA Extraction)

### Directory Layout

```
Kursk/
├── Info/
│   ├── Kursk.desc              # Map metadata
│   ├── Kursk.ai                # AI navigation
│   └── *.dds                   # Loading screen images
├── Gameplay/
│   ├── GameplayObjects.con     # PRIMARY: Object placements
│   ├── ControlPoints.con       # Conquest objectives
│   ├── SpawnPoints.con         # Player spawns
│   ├── AIPathfinding.con       # Bot navigation
│   └── init.con                # Map initialization script
├── Heightdata/
│   ├── HeightMap.raw           # Terrain heightmap (binary)
│   ├── HeightMap.con           # Heightmap configuration
│   └── ColorMap.raw            # Terrain color overlay
├── Textures/
│   ├── Detail/
│   │   └── *.dds               # Detail textures
│   └── *.dds                   # Terrain textures
└── StaticObjects/
    ├── *.sm                    # Static mesh files
    └── *.rs                    # Render state files
```

**Note:** Exact structure may vary between maps and game versions.

## GameplayObjects.con Format

### Object Template Definitions

**Syntax:**
```con
ObjectTemplate.create <ObjectType> <ObjectName>
ObjectTemplate.setNetworkableInfo <NetworkInfo>
ObjectTemplate.saveInSeparateFile 1
ObjectTemplate.addTemplate <ChildTemplate>
ObjectTemplate.setPosition <x>/<y>/<z>
ObjectTemplate.setRotation <pitch>/<yaw>/<roll>
```

**Example:**
```con
rem *** German Bunker at North Base ***
ObjectTemplate.create StaticObject Bunker_North_01
ObjectTemplate.geometry Bunker_German_Medium
ObjectTemplate.setPosition 152.5/12.3/387.9
ObjectTemplate.setRotation 0/45/0
ObjectTemplate.team 1
ObjectTemplate.armour 100
```

### Common Object Types

**Static Objects:**
- `StaticObject` - Buildings, props
- `SimpleObject` - Basic geometry

**Gameplay Objects:**
- `SpawnPoint` - Player spawn location
- `ControlPoint` - Conquest flag
- `ObjectSpawner` - Vehicle/ammo spawner
- `StrategicArea` - Capture zone

**Vehicles:**
- `Tank` - Tank spawner
- `Plane` - Aircraft spawner
- `Ship` - Naval spawner

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

### Control Point Definition

```con
ObjectTemplate.create ControlPoint CP_Name
ObjectTemplate.setNetworkableInfo ControlPointInfo
ObjectTemplate.radius <radius_in_meters>
ObjectTemplate.team <0|1|2>  # 0=Neutral, 1=Axis, 2=Allies
ObjectTemplate.setPosition <x>/<y>/<z>
ObjectTemplate.controlPointName "Display Name"
ObjectTemplate.timeToLoseControl <seconds>
ObjectTemplate.timeToTakeControl <seconds>
```

**Example:**
```con
rem *** Central Control Point ***
ObjectTemplate.create ControlPoint CP_Center
ObjectTemplate.setPosition 256.0/10.5/512.0
ObjectTemplate.radius 30.0
ObjectTemplate.team 0
ObjectTemplate.controlPointName "Village Center"
ObjectTemplate.timeToTakeControl 30
ObjectTemplate.timeToLoseControl 30
```

### Linking Spawn Points to Control Points

```con
ObjectTemplate.create SpawnPoint SP_Center_01
ObjectTemplate.setPosition 250.0/10.0/505.0
ObjectTemplate.controlPointId <CP_Id>
ObjectTemplate.setSpawnRotation 0/90/0
```

## SpawnPoints.con Format

### Spawn Point Types

1. **Infantry Spawn:**
```con
ObjectTemplate.create SpawnPoint SP_Axis_01
ObjectTemplate.setPosition <x>/<y>/<z>
ObjectTemplate.setSpawnRotation <pitch>/<yaw>/<roll>
ObjectTemplate.team 1
ObjectTemplate.spawnDelay 5
```

2. **Vehicle Spawn:**
```con
ObjectTemplate.create ObjectSpawner VS_Tank_01
ObjectTemplate.setPosition <x>/<y>/<z>
ObjectTemplate.setRotation 0/<yaw>/0
ObjectTemplate.objectTemplate <VehicleTemplate>
ObjectTemplate.team 1
ObjectTemplate.respawnTime 60
ObjectTemplate.maxSpawns -1  # Infinite
ObjectTemplate.timeUntilFirstSpawn 30
```

## HeightMap.raw Format

**Format**: Binary raw data
**Structure**:
- 16-bit unsigned integers (little-endian)
- Resolution: Typically 1024x1024 or 512x512
- Value range: 0-65535
- Maps to height in meters via scale factor

**Metadata** (from HeightMap.con):
```con
HeightmapCluster.setHeightmap Heightdata/HeightMap.raw
HeightmapCluster.setDimensions 1024 1024
HeightmapCluster.setHorizontalScale 2.0
HeightmapCluster.setVerticalScale 0.5
HeightmapCluster.waterLevel 10.0
```

**Conversion Formula:**
```
actual_height = (raw_value / 65535.0) * verticalScale * maxHeight
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

### Phase 1 (Current): Understanding

1. Extract RFA files using BGA
2. Analyze .con file syntax
3. Identify object types and properties
4. Document coordinate ranges

### Phase 2: Asset Cataloging

1. List all BF1942 object types in Kursk
2. Cross-reference with BF6 available assets
3. Create initial mapping database

### Phase 3: Conversion Implementation

1. Write .con parser in Python
2. Extract object positions and types
3. Map to BF6 equivalents
4. Generate .tscn output

### Phase 4: Testing

1. Generate Kursk .tscn
2. Load in Godot
3. Verify positions and mappings
4. Iterate and refine

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

## References

- BF1942 Modding Tutorials: https://bfmods.com/mdt/
- RFA Format Overview: https://www.realtimerendering.com/erich/bf1942/mdt/tutorials/Overview/Overview.html
- BGA Tool: https://github.com/yann-papouin/bga

---

**Last Updated:** October 2025
**Status:** Technical reference - accurate for BF1942 file formats
