# BF6 Portal Asset Catalog - Kursk Conversion

## Executive Summary

**Analysis Date:** 2025-10-10
**Assets Analyzed:** 6,292 total BF6 Portal assets
**Kursk Requirements:** 18 vehicle spawners, 4 control points, terrain, HQs

**Critical Finding:** ✅ ALL required gameplay objects and modern vehicles are UNRESTRICTED
**Terrain Strategy:** Use existing BF6 map terrain (cannot import custom heightmaps)

---

## Asset Library Statistics

### Overview
```
Total Assets:          6,292
Unrestricted:          1,284 (20.4%)  ← Can use on ANY map
Restricted:            5,008 (79.6%)  ← Map-specific only
Unique Categories:     11
```

### Category Breakdown
```
1. Generic              2,756 assets  (43.8%)
2. Architecture           920 assets  (14.6%)
3. Audio                  778 assets  (12.4%)
4. Props                  601 assets  (9.6%)
5. Uncategorized          532 assets  (8.5%)
6. FX                     325 assets  (5.2%)
7. Nature                 176 assets  (2.8%)
8. Backdrop               124 assets  (2.0%)
9. LightFixtures           44 assets  (0.7%)
10. Gameplay               32 assets  (0.5%)
11. Entities                4 assets  (0.1%)
```

### Vehicle & Gameplay Assets
```
Total Vehicle Spawners:   85
Total Terrain Assets:     62
Total Gameplay Objects:   68
```

---

## Kursk-Specific Asset Requirements

### 1. Gameplay Objects (ALL UNRESTRICTED ✅)

#### Core Requirements

| Asset Type | Status | Restrictions | Purpose |
|------------|--------|--------------|---------|
| `HQ_PlayerSpawner` | ✅ Available | UNRESTRICTED | Team base HQ |
| `SpawnPoint` | ✅ Available | UNRESTRICTED | Infantry spawn |
| `CapturePoint` | ✅ Available | UNRESTRICTED | Control point |
| `CombatArea` | ✅ Available | UNRESTRICTED | Playable boundary |
| `VehicleSpawner` | ✅ Available | UNRESTRICTED | Vehicle spawner |
| `DeployCam` | ✅ Available | UNRESTRICTED | Deploy camera |

**Analysis:** Perfect! All core gameplay systems are available without restrictions.

#### Optional Gameplay Objects

| Asset Type | Purpose | Restrictions |
|------------|---------|--------------|
| `AI_Spawner` | Bot spawning | UNRESTRICTED |
| `AreaTrigger` | Custom triggers | UNRESTRICTED |
| `InteractPoint` | Interactive objects | UNRESTRICTED |
| `WorldIcon` | In-world markers | UNRESTRICTED |
| `Sector` | Sector system | UNRESTRICTED |

---

### 2. Vehicles (ALL UNRESTRICTED ✅)

#### Ground Vehicles - Tanks

**BF1942 Requirement:** Light tanks, heavy tanks

| BF6 Asset | Type | Restrictions | Kursk Mapping |
|-----------|------|--------------|---------------|
| `VEH_Abrams` | Main Battle Tank (US) | UNRESTRICTED | Heavy tank (Allies) |
| `VEH_Leopard` | Main Battle Tank (GER) | UNRESTRICTED | Heavy tank (Axis) |

**Recommendation:**
- Axis heavy tanks → `VEH_Leopard` (German MBT)
- Allies heavy tanks → `VEH_Abrams` (US MBT)
- Both teams' light tanks → Use same MBT, differentiate by respawn time

#### Ground Vehicles - Infantry Fighting Vehicles (IFV)

**BF1942 Requirement:** APCs, scout cars

| BF6 Asset | Type | Restrictions | Kursk Mapping |
|-----------|------|--------------|---------------|
| `VEH_CV90` | Infantry Fighting Vehicle | UNRESTRICTED | APC replacement |
| `VEH_Vector` | Light Armored Vehicle | UNRESTRICTED | Scout car replacement |

**Recommendation:**
- APCs → `VEH_CV90` (modern IFV)
- Scout cars → `VEH_Vector` (fast recon vehicle)

#### Ground Vehicles - Light Transport

**BF1942 Requirement:** None originally, but useful

| BF6 Asset | Type | Restrictions | Kursk Mapping |
|-----------|------|--------------|---------------|
| `VEH_Quadbike` | Fast transport | UNRESTRICTED | Optional: Quick transport |

#### Aircraft

**BF1942 Requirement:** Fighters, dive bombers

| BF6 Asset | Type | Restrictions | Kursk Mapping |
|-----------|------|--------------|---------------|
| `VEH_F16` | Multi-role Fighter | UNRESTRICTED | Fighter replacement |
| `VEH_F22` | Air Superiority Fighter | UNRESTRICTED | Fighter replacement (advanced) |
| `VEH_AH64E` | Attack Helicopter | UNRESTRICTED | Dive bomber replacement |
| `VEH_Eurocopter` | Utility Helicopter | UNRESTRICTED | Alternative transport |
| `VEH_JAS39` | Multi-role Fighter | UNRESTRICTED | Alternative fighter |
| `VEH_UH60` | Transport Helicopter | UNRESTRICTED | Troop transport |

**Recommendation:**
- BF1942 Fighters → `VEH_F16` (modern equivalent)
- BF1942 Dive Bombers → `VEH_AH64E` (Apache attack helicopter)
  - Helicopters better suited for ground attack in modern setting
  - Maintains air-to-ground role from original dive bombers

**Alternative:** Could use `VEH_F22` for fighters if wanting more powerful air superiority

#### Static Weapons

**BF1942 Requirement:** AA guns, artillery

| BF6 Asset | Type | Restrictions | Kursk Mapping |
|-----------|------|--------------|---------------|
| `VEH_Stationary_GDF009` | Stationary AA Gun | UNRESTRICTED | AA gun replacement |
| `VEH_Stationary_BGM71TOW` | Stationary AT Launcher | UNRESTRICTED | Artillery alternative |
| `VEH_M2MG` | Stationary Machine Gun | UNRESTRICTED | Defensive emplacement |
| `VEH_Gepard` | Mobile AA | UNRESTRICTED | Alternative AA |
| `VEH_Cheetah` | Mobile AA | UNRESTRICTED | Alternative AA |

**Recommendation:**
- AA Guns → `VEH_Stationary_GDF009` (direct replacement)
- Artillery → `VEH_Stationary_BGM71TOW` (closest static weapon)
  - Note: True artillery may not be available; TOW is anti-tank
  - May need to use vehicle-based artillery or omit

**Challenge:** BF6 may not have traditional artillery spawners. Options:
1. Use `VEH_Stationary_BGM71TOW` as defensive emplacement
2. Replace with additional vehicle spawners
3. Omit artillery, maintain balance differently

---

### 3. Terrain Options

#### Available BF6 Maps (Potential Terrain Sources)

| Map Name | Theme | Suitability for Kursk |
|----------|-------|----------------------|
| `MP_Outskirts` | Open terrain | ⭐⭐⭐ BEST - Open fields |
| `MP_Aftermath` | Urban/damaged | ⭐⭐ Moderate - Mixed terrain |
| `MP_Battery` | Coastal/military | ⭐⭐ Moderate - Open areas |
| `MP_Limestone` | Desert/rocky | ⭐ Low - Wrong biome |
| `MP_FireStorm` | Tropical/jungle | ❌ Not suitable |
| `MP_Abbasid` | Middle East | ❌ Not suitable |
| `MP_Dumbo` | Urban | ❌ Not suitable |
| `MP_Tungsten` | Industrial | ❌ Not suitable |
| `MP_Capstone` | Unknown | ❓ Unknown |

**Recommendation:** Use `MP_Outskirts` terrain
- Open terrain matches Kursk's rolling plains
- Relatively flat with gentle elevation changes
- European/temperate aesthetic closest to Russian steppe

#### Terrain Assets Available

```
TerrainAsset_Gibraltar_02 through TerrainAsset_Gibraltar_24 (23 variants)
```

**Note:** These are terrain mesh pieces, not full heightmaps. Terrain is pre-built per map.

**Implication:** We cannot import Kursk's heightmap. Options:
1. ✅ **Use MP_Outskirts terrain as-is** (simplest)
2. Create custom terrain in Godot (complex, may not export)
3. Request terrain from map that best matches Kursk topography

---

### 4. Static Objects & Props

#### Nature Assets (Trees, Vegetation)

**BF1942 Kursk has:** Russian plains vegetation, sparse trees

**BF6 Available:**
- Nature category: 176 assets
- Most are map-restricted
- Generic/Common/Nature: Likely available

**Strategy:**
- Use unrestricted nature assets from Generic/Common
- Avoid map-specific vegetation
- Phase 3 will catalog specific usable trees/bushes

#### Architecture & Props

**BF1942 Kursk has:** Minimal buildings (lumber mill, bunkers)

**BF6 Available:**
- Architecture: 920 assets
- Props: 601 assets
- Generic categories: 2,756 assets

**Challenge:** Most architecture is map-specific

**Strategy:**
1. Identify unrestricted buildings in Generic/Common
2. Map BF1942 structures to closest BF6 equivalents
3. Accept aesthetic differences (modern vs WW2)
4. Focus on functional placement over perfect visual match

---

## Object Mapping Table (BF1942 → BF6)

### Vehicle Spawners

| BF1942 Object | Count | BF6 Replacement | Notes |
|---------------|-------|-----------------|-------|
| `lighttankspawner` | 4 | `VEH_Leopard` / `VEH_Abrams` | Use team-appropriate MBT |
| `heavytankspawner` | 3 | `VEH_Leopard` / `VEH_Abrams` | Same as light (modern MBTs) |
| `APCSpawner` | 2 | `VEH_CV90` | IFV replacement |
| `ScoutCarSpawner` | 2 | `VEH_Vector` | Light vehicle |
| `FighterSpawner` | 2 | `VEH_F16` | Multi-role fighter |
| `DiveBomberSpawner` | 2 | `VEH_AH64E` | Attack helicopter |
| `AAGunSpawner` | 1 | `VEH_Stationary_GDF009` | Static AA |
| `ArtillerySpawner` | 2 | `VEH_Stationary_BGM71TOW` | Static AT (no true artillery) |

**Total:** 18 spawners → 18 BF6 vehicle spawners

### Gameplay Objects

| BF1942 Object | Count | BF6 Replacement | Notes |
|---------------|-------|-----------------|-------|
| Control Points | 4 | `CapturePoint` | Direct mapping |
| Axis Base | 1 | `HQ_PlayerSpawner` (Team 1) | With 4+ `SpawnPoint` |
| Allies Base | 1 | `HQ_PlayerSpawner` (Team 2) | With 4+ `SpawnPoint` |
| Map Boundary | 1 | `CombatArea` + `PolygonVolume` | Define playable area |

---

## Coordinate Transformation Notes

### BF1942 Kursk Coordinates

**From analysis:**
- X-axis range: 437.315 to 639.658 (~202 meters)
- Y-axis range: 76.6406 to 94.12 (~17.5 meters elevation)
- Z-axis range: 238.39 to 849.956 (~611 meters)

**Map dimensions:** ~200m x 600m

### BF6 Coordinate System

**From MP_Outskirts example:**
- Uses same Y-up, right-handed system
- Units in meters
- Transform3D matrices for rotation

**Transformation Required:**
1. Direct position mapping (x, y, z) → (x, y, z)
2. Rotation conversion: BF1942 Euler (pitch/yaw/roll) → Transform3D matrix
3. Possible origin shift to center map appropriately

**Scale Factor:** 1:1 (both use meters)

---

## Level Restriction Analysis

### Most Restricted Maps (Assets Locked)
```
1. MP_Dumbo     - 1,514 unique assets
2. MP_Aftermath - 1,452 unique assets
3. MP_Abbasid   - 1,354 unique assets
4. MP_Battery   - 1,232 unique assets
```

**Implication:** Cannot use 75-80% of assets if targeting specific maps

**Kursk Strategy:** Use ONLY unrestricted assets (1,284 available)
- Ensures portability
- Avoids dependency on specific map terrains
- Allows future expansion to other BF1942 maps

---

## Phase 2 Conclusions

### ✅ What We Have (Good News)

1. **All core gameplay objects are unrestricted**
   - HQs, spawn points, capture points, combat areas
   - Can build fully functional Conquest map

2. **All modern vehicles are unrestricted**
   - Tanks, IFVs, helicopters, jets, static weapons
   - 10 distinct vehicle types available

3. **Clear object mapping path**
   - Each BF1942 spawner has modern equivalent
   - Functional roles preserved (tanks, air support, AA, etc.)

### ⚠️ Challenges Identified

1. **No custom terrain import**
   - Must use existing BF6 map terrain
   - Recommend: MP_Outskirts (open terrain)
   - Accept: Won't match Kursk heightmap exactly

2. **Artillery replacement imperfect**
   - No true artillery spawners in BF6
   - Best alternative: Static TOW launcher
   - May need to balance differently

3. **Static objects mostly map-restricted**
   - Limited unrestricted buildings/props
   - Will rely on Generic/Common assets
   - Aesthetic will be modern, not WW2

4. **Terrain elevation limited**
   - Kursk ~17m elevation change
   - BF6 maps pre-built
   - Manual terrain sculpting not possible in Portal

### 📋 Phase 3 Requirements

Based on Phase 2 analysis, Phase 3 must:

1. **Create BF1942 → BF6 mapping database**
   - JSON file with exact object mappings
   - Include vehicle types, properties, respawn times
   - Document any gameplay balance adjustments

2. **Build .con parser**
   - Extract positions, rotations, teams, IDs
   - Handle multiple file formats (Conquest/, etc.)
   - Validate data completeness

3. **Implement coordinate transformer**
   - Convert BF1942 Euler angles → Godot Transform3D
   - Apply any origin shifts needed
   - Preserve spatial relationships

4. **Generate .tscn template builder**
   - Create HQ_PlayerSpawner nodes with spawn points
   - Place VehicleSpawner nodes at correct positions
   - Generate CapturePoint nodes
   - Define CombatArea polygon from map bounds
   - Reference MP_Outskirts terrain

5. **Create validation tools**
   - Check minimum spawn points (4 per team)
   - Verify all positions within combat area
   - Validate Transform3D matrices
   - Ensure ObjId uniqueness

---

## Recommended Terrain Selection: MP_Outskirts

**Rationale:**
- Open terrain similar to Russian steppe
- Relatively flat (good for tank battles)
- Minimal urban clutter
- Temperate climate aesthetic
- Best available match for Kursk

**Terrain Files:**
- `GodotProject/static/MP_Outskirts_Terrain.tscn`
- `GodotProject/static/MP_Outskirts_Assets.tscn`

**Usage in Kursk.tscn:**
```gdscript
[node name="Static" type="Node3D" parent="."]

[node name="MP_Outskirts_Terrain" parent="Static" instance=ExtResource("MP_Outskirts_Terrain.tscn")]

[node name="MP_Outskirts_Assets" parent="Static" instance=ExtResource("MP_Outskirts_Assets.tscn")]
```

**Note:** Will need to adjust spawn positions to match terrain elevation

---

## Asset Availability Summary

### Unrestricted Assets by Category (Usable for Kursk)

```
Generic:              ~600 unrestricted
Architecture:         ~50 unrestricted
Props:                ~150 unrestricted
Nature:               ~30 unrestricted
Gameplay:             32 (all unrestricted)
Vehicles:             10 modern vehicles (unrestricted)
```

**Total Usable Assets:** ~1,284 (20% of library)

**Sufficient for Kursk:** ✅ YES
- Core gameplay complete
- Vehicle variety adequate
- Enough props for basic scenery
- Terrain available (MP_Outskirts)

---

## Next Phase Preview

**Phase 3 Tasks:**
1. Create `tools/object_mapping_database.json`
2. Write `tools/parse_kursk_data.py` (.con parser)
3. Write `tools/coordinate_transform.py` (math utilities)
4. Write `tools/generate_kursk_tscn.py` (main converter)
5. Test on Kursk data
6. Validate output .tscn
7. Manual refinement in Godot

**Estimated Complexity:** Medium-High
- Parsing: Straightforward (text .con files)
- Coordinate math: Well-defined transformations
- .tscn generation: Template-based, manageable
- Testing: Iterative validation required

---

*Document Status:* Complete
*Phase:* Phase 2 - Asset Cataloging
*Next Step:* Commit Phase 2, begin Phase 3
*Last Updated:* 2025-10-10
