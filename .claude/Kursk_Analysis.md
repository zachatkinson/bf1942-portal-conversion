# Kursk Map Analysis

## Extraction Status

✅ **Successfully extracted from RFA archives**

Location: `bf1942_source/extracted/Kursk/`

## Map Overview

**Map Name:** Kursk
**Game Mode Analyzed:** Conquest
**Teams:**
- Team 1: Axis (Germany)
- Team 2: Allies (Russia)

**Camera Position:** 354.82/94.12/451.787

## Control Points (4 Total)

### 1. Axis Base 1
```
Name: AxisBase_1_Cpoint
Position: 437.315/77.8547/238.39
Team: 1 (Axis)
Type: Main base
```

### 2. Allies Base 2
```
Name: AlliesBase_2_Cpoint
Position: 568.058/76.6406/849.956
Team: 2 (Allies)
Type: Main base
```

### 3. Lumber Mill (Neutral)
```
Name: openbase_lumbermill_Cpoint
Position: 639.658/83.3344/556.038
Team: Neutral (capturable)
Type: Neutral control point
```

### 4. Central Ammo Point (Neutral)
```
Name: openbasecammo
Position: 508.833/84.8718/582.2
Team: Neutral (capturable)
Type: Neutral control point
```

## Map Dimensions

Based on control point positions:

**X-axis range:** 437.315 to 639.658 (~202 meters)
**Y-axis range:** 76.6406 to 94.12 (~17.5 meters elevation change)
**Z-axis range:** 238.39 to 849.956 (~611 meters)

**Approximate Map Size:** 202m x 611m (relatively small, open terrain map)

## Vehicle Spawners by Base

### Axis Base 1 (Team 1)

**Tanks:**
- Light tank #1: 450.345/78.6349/249.093 (rotation: 0/0.103998/1.52588e-005)
- Light tank #2: 444.421/78.6286/248.701 (rotation: 1.27288/0.170019/-1.52588e-005)
- Heavy tank: 388.567/78.7631/246.062 (rotation: 0/-0.664717/-1.52588e-005)

**Vehicles:**
- APC: 449.911/79.0704/234.584 (rotation: 0/1.17886/1.52588e-005)
- Scout car: 409.739/78.1727/233.916 (rotation: -92.664/-0.0204939/-0.409744)

**Aircraft:**
- Fighter: 376.687/79.0611/203.812 (rotation: 91.616/-12.871/1.52588e-005)
- Dive bomber: 374.75/79.857/216.141 (rotation: 98.5421/-8.4672/0.602325)

**Total Axis spawners:** 7

### Allies Base 2 (Team 2)

**Tanks:**
- Heavy tank: 594.427/78.4077/871.696 (rotation: 89.1573/0.0152983/-0.618668)
- Light tank #1: 574.056/77.7991/849.572 (rotation: -177.84/-0.132352/-1.52588e-005)
- Light tank #2: 563.023/77.8716/843.171 (rotation: 179.352/-0.0754579/1.52588e-005)

**Vehicles:**
- Scout car: 562.049/77.4702/868.331 (rotation: 179.352/-0.441373/1.52588e-005)
- APC: 580.677/78.2001/872.065 (rotation: -89.6219/0.0103454/-1.16164)

**Aircraft:**
- Fighter: 490.64/79.15/899.592 (rotation: 90.3638/-10.3916/-1.58968)
- Dive bomber: 495.157/78.1042/884.279 (rotation: 91.616/-12.871/1.52588e-005)

**Total Allies spawners:** 7

### Lumber Mill (Neutral Base 3)

**Static Weapons:**
- AA Gun: 684.391/93.4701/553.988 (rotation: -90.792/0/1.52588e-005)
- Artillery #1: 635.281/83.6894/552.097 (rotation: -91.119/0.0968891/0.690414)
- Artillery #2: 634.986/83.7747/560.106 (rotation: -89.8568/0.1112/0.691544)

**Total neutral spawners:** 3

### Central Ammo (Neutral Base 4)

**Vehicles:**
- Heavy tank: 496.456/85.524/583.978 (rotation: -171.783/0.66694/1.52588e-005)

**Total neutral spawners:** 1

## BF1942 Object Types Found

**Vehicle Spawners:**
- `lighttankspawner` - Light tank spawner
- `heavytankspawner` - Heavy tank spawner
- `APCSpawner` - Armored personnel carrier
- `ScoutCarSpawner` - Scout/recon vehicle
- `FighterSpawner` - Fighter aircraft
- `DiveBomberSpawner` - Bomber aircraft

**Static Weapons:**
- `AAGunSpawner` - Anti-aircraft gun
- `ArtillerySpawner` - Artillery piece

**Control Points:**
- Base control points (linked to team spawners)
- Neutral control points (capturable)

## BF6 Mapping Requirements

### Required BF6 Components

1. **Team HQs (2)**
   - TEAM_1_HQ at Axis base position
   - TEAM_2_HQ at Allies base position
   - Each needs minimum 4 infantry spawn points

2. **CapturePoints (4)**
   - Map the 4 control points
   - Set initial ownership (Axis, Allies, or Neutral)
   - Define capture radius

3. **VehicleSpawners (18 total)**
   - Need BF6 equivalent vehicles:
     - Light tanks → Modern light armor
     - Heavy tanks → Modern MBTs
     - APCs → Modern APCs
     - Scout cars → Modern light vehicles
     - Fighters → Modern jets/helicopters?
     - Dive bombers → Modern ground attack aircraft?
     - AA guns → Static AA
     - Artillery → Static artillery

4. **Combat Area**
   - Define polygon around playable area
   - Based on map dimensions: ~200m x 600m

5. **Terrain**
   - Select closest BF6 terrain (open, flat Russian plains)
   - Manual sculpting for elevation changes (~17m variation)

## Conversion Challenges

### 1. Aircraft
**Issue:** BF6 Portal may not have WW2 aircraft
**Solution:**
- Option A: Use modern aircraft equivalents
- Option B: Omit aircraft spawners, focus on ground vehicles
- Option C: Replace with modern helicopters

### 2. Static Weapons
**Issue:** AA guns and artillery may be vehicle-based in BF6, not static
**Solution:** Map to closest interactive object or vehicle spawner

### 3. Team Balance
**Issue:** Both teams have identical 7 spawners - maintain balance
**Solution:** Ensure BF6 equivalent vehicles maintain parity

### 4. Neutral Control Points
**Issue:** Lumber Mill has 3 spawners, Ammo has 1
**Solution:** Map spawners to capture point, verify BF6 supports spawner linking

## Next Steps

### Phase 2: BF6 Asset Cataloging
1. Search `asset_types.json` for vehicle spawners
2. Identify modern tank equivalents
3. Find APC/transport options
4. Determine aircraft availability
5. Locate capture point assets
6. Find terrain options (Russian plains theme)

### Phase 3: Object Mapping
Create mapping database:
```
BF1942                  →  BF6 Equivalent
----------------------------------------------
lighttankspawner        →  [Find modern light tank]
heavytankspawner        →  [Find modern MBT]
APCSpawner              →  [Find modern APC]
ScoutCarSpawner         →  [Find modern light vehicle]
FighterSpawner          →  [TBD - aircraft availability]
DiveBomberSpawner       →  [TBD - ground attack aircraft]
AAGunSpawner            →  [Find AA weapon/vehicle]
ArtillerySpawner        →  [Find artillery]
```

### Phase 4: Generate .tscn
- Place 2 HQ_PlayerSpawners
- Generate 8+ infantry spawn points (4 per team minimum)
- Place 4 CapturePoint objects
- Place 18 VehicleSpawner objects with transforms
- Define CombatArea polygon
- Reference BF6 terrain

## File Structure Notes

**Conquest mode files:**
- `Conquest/ControlPoints.con` - Control point definitions
- `Conquest/ObjectSpawns.con` - Vehicle/weapon spawners
- `Conquest/ObjectSpawnTemplates.con` - Spawner templates

**Other modes:** CTF, TDM, SinglePlayer (not prioritized)

**Init files:**
- `Init.con` - Map initialization, teams, kits, lighting
- `AIpathFinding.con` - Bot navigation (not needed for Portal)
- `AI/` directory - Bot strategies (not needed for Portal)

---

*Last Updated*: 2025-10-10
*Status*: Kursk extraction and analysis complete
*Next Phase*: Phase 2 - BF6 asset cataloging
