# BF1942 Base Game Vehicle Analysis

**Scan Date:** 2025-10-15
**Maps Scanned:** 20 (Battle_of_Britain through Wake)
**Total Unique Vehicles:** 46

---

## Vehicle Categories

### Land Vehicles

#### Tanks
- **heavytankspawner** / **HeavyTankSpawner** - Heavy tanks (Tiger, IS-2, etc.)
- **lighttankspawner** / **LightTankSpawner** - Light tanks (Panzer IV, T-34, M4 Sherman)
- **TankSpawner** - Generic tank spawner
- **ShermanSpawner** / **shermanSpawner** - M4 Sherman tank
- **chi-haSpawner** - Type 97 Chi-Ha (Japanese tank)

#### Armored Personnel Carriers & Scout Vehicles
- **APC** / **APCSpawner** - Armored Personnel Carrier (Hanomag, M3 Halftrack)
- **ScoutCarSpawner** - Scout cars (Kübelwagen, Willys MB)
- **willyspawner** - Willys MB Jeep (Allies)
- **Jeep** - Generic jeep spawner

#### Artillery & Anti-Aircraft
- **ArtillerySpawner** - Artillery pieces (Wespe, Priest, etc.)
- **AAGunSpawner** - Anti-aircraft guns (Flak 38, Bofors)
- **AlliesAASpawner** - Allied AA gun spawner
- **AxisAASpawner** - Axis AA gun spawner
- **PAK40Spawner** - PAK 40 anti-tank gun

#### Static Defenses
- **MachinegunSpawner** - Static machine gun nests
- **CDNMachinegunSpawner** - Canadian machine gun variant
- **DefgunSpawner** - Defensive gun emplacements

---

### Aircraft

#### Fighters
- **Fighter** - Generic fighter spawner
- **FighterSpawner** - Fighter aircraft (Spitfire, BF-109, Zero)

#### Bombers
- **DiveBomberSpawner** - Dive bombers (Stuka, SBD Dauntless)
- **HeavyBomberSpawner** - Heavy bombers (B-17, Lancaster)
- **LevelBomberSpawner** / **levelBomberSpawner** - Level bombers
- **torpedoBomberSpawner** - Torpedo bombers (for naval strikes)

#### Special Aircraft
- **ParatroopSpawner** - Paratroop transport aircraft

---

### Naval Vessels

#### Capital Ships
- **battleshipSpawner** - Battleships (Prince of Wales, Yamato)
- **carrierSpawner** / **carrierSpawner_1** / **carrierSpawner_2** - Aircraft carriers

#### Support Ships
- **DestroyerSpawner** / **DestroyerSpawner2** - Destroyer vessels
- **SubmarineSpawner** - Submarine

#### Landing Craft
- **lcvpSpawner** - LCVP landing craft (Higgins boat)
- **PTLCVPSpawner** - PT boat variant of LCVP
- **ptBoatSpawner** - PT boat (motor torpedo boat)
- **RaftSpawner** - Assault rafts

---

### Special Structures

#### Battle of Britain Special
- **Britain_FactorySpawner** - Factory building spawner
- **RadarTowerSpawner** - Generic radar tower
- **Clacton_RadarTower_Spawner** - Clacton radar installation
- **East_Harwick_RadarTower_Spawner** - East Harwick radar
- **Felixstowe_RadarTower_Spawner** - Felixstowe radar
- **West_Harwick_RadarTower_Spawner** - West Harwick radar

---

## Maps by Theater

### European Theater (Western Front)
- **Battle_of_the_Bulge** - 9 vehicles (Ardennes, 1944)
- **Bocage** - 11 vehicles (Normandy hedgerow country, 1944)
- **Liberation_of_Caen** - 11 vehicles (Normandy, 1944)
- **Market_Garden** - 12 vehicles (Netherlands, 1944)
- **Omaha_Beach** - 14 vehicles (D-Day invasion, 1944)

### European Theater (Eastern Front)
- **Berlin** - 9 vehicles (Final assault on Berlin, 1945)
- **Kharkov** - 9 vehicles (Soviet-German battles, 1942-43)
- **Kursk** - 9 vehicles (Largest tank battle, 1943)
- **Stalingrad** - 9 vehicles (Urban warfare, 1942-43)

### North African Theater
- **Battleaxe** - 11 vehicles (Operation Battleaxe, 1941)
- **El_Alamein** - 11 vehicles (Desert campaign, 1942)
- **Gazala** - 11 vehicles (Gazala Line, 1942)
- **Tobruk** - 8 vehicles (Siege of Tobruk, 1941)

### Pacific Theater (Island Warfare)
- **GuadalCanal** - 14 vehicles (First major offensive, 1942-43)
- **Invasion_of_the_Philippines** - 16 vehicles (Liberation, 1944-45)
- **Iwo_Jima** - 14 vehicles (Iconic flag-raising battle, 1945)
- **Wake** - 13 vehicles (Wake Island defense, 1941)

### Pacific Theater (Naval)
- **Coral_sea** - 18 vehicles (Carrier battle, 1942)
- **Midway** - 16 vehicles (Turning point, 1942)

### Air Warfare
- **Battle_of_Britain** - 13 vehicles (RAF vs Luftwaffe, 1940)

---

## Vehicle Distribution by Map

### Most Vehicle-Heavy Maps
1. **Coral_sea** - 18 vehicles (carrier warfare with full naval/air complement)
2. **Invasion_of_the_Philippines** - 16 vehicles (combined arms amphibious assault)
3. **Midway** - 16 vehicles (carrier battle with destroyers, subs, aircraft)
4. **GuadalCanal** - 14 vehicles (island warfare with naval support)
5. **Iwo_Jima** - 14 vehicles (amphibious assault with battleship support)
6. **Omaha_Beach** - 14 vehicles (D-Day with landing craft and air support)

### Lightest Vehicle Maps
1. **Tobruk** - 8 vehicles (primarily desert tank warfare)
2. **Battle_of_the_Bulge** - 9 vehicles (winter tank/infantry combat)
3. **Berlin** - 9 vehicles (urban tank warfare)
4. **Kharkov** - 9 vehicles (Eastern Front tank battles)
5. **Kursk** - 9 vehicles (focused tank warfare)
6. **Stalingrad** - 9 vehicles (urban close-quarters combat)

---

## Common Vehicle Patterns

### Standard Land Warfare Loadout (9-11 vehicles)
Most European theater maps include:
- Light tanks
- Heavy tanks
- APCs
- Scout cars
- Artillery
- AA guns
- Machine guns
- Fighters
- Dive bombers

### Amphibious Assault Loadout (12-14 vehicles)
Pacific island maps add:
- Landing craft (LCVP)
- Destroyers
- Defensive guns
- Carrier support

### Full Naval Warfare Loadout (16-18 vehicles)
Coral Sea and Midway include:
- Multiple carriers
- Battleships
- Destroyers
- Submarines
- Full air wings (fighters, dive bombers, torpedo bombers)
- PT boats

### Special Case: Battle of Britain (13 vehicles)
Unique to this map:
- Radar towers (4 named installations)
- Factory spawner
- Focus on air combat infrastructure

---

## Case Sensitivity Issues

**Note:** BF1942 has inconsistent naming conventions. The following duplicates exist:

- `HeavyTankSpawner` vs `heavytankspawner`
- `LightTankSpawner` vs `lighttankspawner`
- `LevelBomberSpawner` vs `levelBomberSpawner`
- `ShermanSpawner` vs `shermanSpawner`
- `APCSpawner` vs `APC`
- `FighterSpawner` vs `Fighter`
- `Jeep` vs `willyspawner`

These are likely the same vehicle types with different naming conventions used across different maps or game versions.

---

## Portal Conversion Implications

### High Priority for Portal SDK
1. **Land Vehicles** - Essential for all map types
   - Tanks (light/heavy)
   - Scout cars/jeeps
   - APCs

2. **Aircraft** - Critical for authentic BF1942 experience
   - Fighters
   - Dive bombers
   - Heavy bombers

3. **Static Defenses** - Core gameplay elements
   - Machine gun nests
   - Artillery
   - AA guns

### Medium Priority
1. **Naval Vessels** - Only 6 maps require these
   - Destroyers
   - Landing craft (LCVP)
   - Carriers (for Coral Sea/Midway/Wake/Iwo Jima/GuadalCanal)

### Low Priority (Map-Specific)
1. **Specialized Units**
   - Radar towers (Battle of Britain only)
   - Submarines (Coral Sea, Midway, GuadalCanal)
   - PT boats (Philippines, Wake, Midway)
   - Factory spawner (Battle of Britain only)

### Conversion Challenges

**Naval Maps**: 6 maps heavily depend on naval vehicles:
- Coral_sea, Midway, Wake, Iwo_Jima, GuadalCanal, Invasion_of_the_Philippines
- May need to skip or heavily modify if Portal lacks naval assets

**Air-Focused Maps**: Battle of Britain is unique:
- Relies on radar towers and factory structures
- May be difficult to recreate authentically in Portal

**Easiest Conversions**: Land-focused maps (9-11 vehicles)
- Tobruk, Berlin, Kharkov, Kursk, Stalingrad
- Use only standard land vehicles that Portal likely supports

---

## Next Steps for Portal SDK

1. **Map BF1942 vehicle names to Portal equivalents**
   - Create mapping file: `bf1942_to_portal_vehicles.json`
   - Research Portal vehicle catalog in `asset_types.json`

2. **Categorize maps by conversion difficulty**
   - Easy: Land-only maps (Tobruk, Kursk, Stalingrad)
   - Medium: Combined arms (Bocage, El Alamein, Battleaxe)
   - Hard: Naval-dependent (Coral Sea, Midway, Wake)

3. **Test vehicle spawning system**
   - Verify ObjectSpawner → Portal vehicle spawner conversion
   - Test spawn points, team ownership, respawn timers

4. **Document unsupported vehicles**
   - Identify which BF1942 vehicles have no Portal equivalent
   - Plan workarounds (skip, replace with similar vehicle, etc.)

---

**Files Generated:**
- `/Users/zach/Downloads/PortalSDK/tools/bf1942_vehicle_scan_results.json` - Raw scan data
- `/Users/zach/Downloads/PortalSDK/tools/bf1942_vehicle_categories.md` - This analysis document
- `/Users/zach/Downloads/PortalSDK/tools/scan_bf1942_vehicles.py` - Reusable scan script
