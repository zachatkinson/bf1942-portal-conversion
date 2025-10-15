# BF1942 to BF6 Portal Vehicle Mappings Reference

**Last Updated:** 2025-10-15
**Total Mappings:** 81 BF1942 vehicles → 15 BF6 Portal VehicleTypes
**Coverage:** 93% of available BF6 vehicle types (15/16, F22 unused)

## Table of Contents

1. [Overview](#overview)
2. [Mapping Convention](#mapping-convention)
3. [Complete Vehicle Inventory](#complete-vehicle-inventory)
4. [Mappings by BF6 Vehicle Type](#mappings-by-bf6-vehicle-type)
5. [Mappings by Category](#mappings-by-category)
6. [Special Cases & Notes](#special-cases--notes)
7. [Usage Examples](#usage-examples)

---

## Overview

This document provides a comprehensive reference for all BF1942 to BF6 Portal vehicle mappings used in the conversion pipeline. These mappings transform World War II era vehicles into their modern-day equivalents while maintaining faction alignment and gameplay roles.

### Data Sources

- **Primary Mapper:** `tools/bfportal/mappers/vehicle_mapper.py` (81 mappings)
- **Maps Analyzed:** All 36 BF1942 maps (base game + expansions)
- **BF6 SDK Reference:** VehicleSpawner.gd enum definitions

---

## Mapping Convention

**CRITICAL RULE:** Axis vs Allied faction alignment must be preserved across all theaters.

### Faction Alignment

```
Axis Powers (Germany, Italy, Japan)  → non-NATO modern assets
Allied Powers (USA, UK, USSR)        → NATO/American modern assets
```

### Team Mapping

The BF1942Engine automatically swaps teams during conversion:

```
BF1942 Team 1 (Axis)    → BF6 Portal Team 2 (non-NATO)
BF1942 Team 2 (Allied)  → BF6 Portal Team 1 (NATO/American)
```

### Why This Convention?

1. **Gameplay Balance:** Maintains original faction dynamics
2. **Historical Consistency:** Preserves WW2 power alignments
3. **Asset Availability:** Works with Portal's limited vehicle set
4. **Universal Application:** Applies to ALL theaters (Europe, Pacific, Africa)

---

## Complete Vehicle Inventory

### Axis → non-NATO Mappings

| BF1942 Vehicle | BF6 VehicleType | Category | Theater | Notes |
|----------------|-----------------|----------|---------|-------|
| **German Tanks** |
| Panzer4, PanzerIV | Leopard | Tank | Europe, Africa | Standard medium tank |
| PanzerV, Panther | Leopard | Tank | Europe | Heavy tank variant |
| PanzerVI, Tiger, TigerTank | Leopard | Tank | Europe, Africa | Super-heavy tank |
| **German Tank Destroyers** |
| StuG, StuG3, StuGIII | CV90 | Tank Destroyer | Europe, Africa | Assault gun |
| Wespe | CV90 | Tank Destroyer | Europe | Self-propelled howitzer |
| **German Aircraft** |
| BF109, Bf109, Me109, Messerschmitt | SU57 | Fighter | Europe, Africa | Primary fighter |
| FW190, Focke-Wulf | SU57 | Fighter | Europe | Advanced fighter |
| Ju87, Stuka | Eurocopter | Dive Bomber | Europe, Africa | Ground attack |
| Ju88 | Eurocopter | Dive Bomber | Europe | Medium bomber |
| **Japanese Vehicles** |
| TypeChiHa, Chi-Ha, Type97 | Cheetah | Tank | Pacific | Light tank |
| Zero, A6M | SU57 | Fighter | Pacific | Carrier-based fighter |

### Allied → NATO Mappings

| BF1942 Vehicle | BF6 VehicleType | Category | Theater | Notes |
|----------------|-----------------|----------|---------|-------|
| **American Tanks** |
| Sherman, ShermanTank, M4Sherman, M4A3 | Abrams | Tank | All | Standard medium tank |
| M10, M10Wolverine | Abrams | Tank | Europe, Africa | Tank destroyer variant |
| **Soviet Tanks** |
| T34, T-34, T3485, T-34-85 | Abrams | Tank | Europe | Medium tank |
| KV1, KV-1 | Abrams | Tank | Europe | Heavy tank |
| **British Tanks** |
| Churchill, ChurchillTank | Abrams | Tank | Europe, Africa | Infantry tank |
| Crusader | Abrams | Tank | Africa | Cruiser tank |
| **American SPGs** |
| Priest, M7Priest | M2Bradley | SPG | Europe, Africa | Self-propelled artillery |
| **American Aircraft** |
| P51, P-51, Mustang | F16 | Fighter | Europe, Pacific | Long-range escort fighter |
| **British Aircraft** |
| Spitfire | F16 | Fighter | Europe | Interceptor |
| Lancaster | JAS39 | Bomber | Europe | Heavy bomber |
| **Soviet Aircraft** |
| Yak9, Yak-9 | F16 | Fighter | Europe | Fighter |
| IL2, IL-2, Ilyushin, Sturmovik | AH64 | Dive Bomber | Europe | Ground attack aircraft |
| **American Bombers** |
| B17, B-17 | JAS39 | Bomber | Europe, Pacific | Strategic bomber |

### Universal (All Factions)

| BF1942 Vehicle | BF6 VehicleType | Category | Notes |
|----------------|-----------------|----------|-------|
| **Light Vehicles** |
| Willys, WillysMB, Jeep | Quadbike | Light Vehicle | American light transport |
| Kubelwagen | Quadbike | Light Vehicle | German light transport |
| GAZ, GAZ67 | Quadbike | Light Vehicle | Soviet light transport |
| **APCs & Transports** |
| Hanomag | Vector | APC | German halftrack |
| M3, M3A1, Halftrack | Vector | APC | American halftrack |
| **Anti-Aircraft** |
| Flak38, Flak36, Flak88 | Gepard | Anti-Air | German AA guns |
| WirbelWind | Gepard | Anti-Air | German SPAAG |
| M16, M16AAA | Gepard | Anti-Air | American AA halftrack |
| **Naval & Amphibious** |
| LandingCraft, LCVP, Higgins | Flyer60 | Naval | Landing craft |
| DUKW | Flyer60 | Naval | Amphibious truck |
| **Modern Additions** |
| AttackHeli, Apache, AH64 | AH64 | Attack Helicopter | Not in original BF1942 |
| TransportHeli, BlackHawk, UH60 | UH60 | Transport Helicopter | Not in original BF1942 |

---

## Mappings by BF6 Vehicle Type

### Summary Statistics

```
Type               Count    Percentage    Usage
─────────────────────────────────────────────────
Abrams               15         19%      ████████████████████
SU57                  8         10%      ██████████
Leopard               7          9%      █████████
AH64                  7          9%      █████████
F16                   6          7%      ████████
Gepard                6          7%      ████████
Quadbike              6          7%      ████████
CV90                  4          5%      █████
Flyer60               4          5%      █████
Vector                4          5%      █████
Cheetah               3          4%      ████
Eurocopter            3          4%      ████
JAS39                 3          4%      ████
UH60                  3          4%      ████
M2Bradley             2          2%      ██
F22                   0          0%      (unused)
─────────────────────────────────────────────────
TOTAL                81        100%
```

### Detailed Breakdown

#### Abrams (M1 Abrams Tank) - 15 mappings

**Allied Main Battle Tank** - Used for American, British, and Soviet WW2 tanks.

```
American:
- Sherman, ShermanTank, M4Sherman, M4A3
- M10, M10Wolverine

Soviet:
- T34, T-34, T3485, T-34-85
- KV1, KV-1

British:
- Churchill, ChurchillTank
- Crusader
```

**Rationale:** All Allied heavy/medium tanks map to NATO's premier MBT.

---

#### Leopard (Leopard 2 Tank) - 7 mappings

**Axis Main Battle Tank** - Used for German WW2 tanks.

```
German:
- Panzer4, PanzerIV (Panzer IV)
- PanzerV, Panther (Panther)
- PanzerVI, Tiger, TigerTank (Tiger I)
```

**Rationale:** German armor → German modern MBT (non-NATO faction in Portal).

---

#### SU57 (Sukhoi Su-57) - 8 mappings

**Axis Fighter Aircraft** - Used for German and Japanese fighters.

```
German:
- BF109, Bf109, Me109, Messerschmitt (Messerschmitt Bf 109)
- FW190, Focke-Wulf (Focke-Wulf Fw 190)

Japanese:
- Zero, A6M (Mitsubishi A6M Zero)
```

**Rationale:** Axis air superiority fighters → non-NATO 5th gen fighter.

---

#### AH64 (AH-64 Apache) - 7 mappings

**Allied Ground Attack** - Used for Soviet dive bombers + modern attack helis.

```
Soviet Dive Bombers:
- IL2, IL-2, Ilyushin, Sturmovik (Ilyushin Il-2)

Modern (custom):
- AttackHeli, Apache, AH64
```

**Rationale:** Ground attack role preserved; Allied → NATO attack helicopter.

---

#### F16 (F-16 Fighting Falcon) - 6 mappings

**Allied Fighter Aircraft** - Used for American, British, and Soviet fighters.

```
American:
- P51, P-51, Mustang (P-51 Mustang)

British:
- Spitfire (Supermarine Spitfire)

Soviet:
- Yak9, Yak-9 (Yakovlev Yak-9)
```

**Rationale:** Allied air superiority fighters → NATO multirole fighter.

---

#### Gepard (Flakpanzer Gepard) - 6 mappings

**Anti-Aircraft Vehicles** - Used for all WW2 AA systems.

```
German:
- Flak38, Flak36, Flak88 (stationary AA)
- WirbelWind (mobile SPAAG)

American:
- M16, M16AAA (M16 Multiple Gun Motor Carriage)
```

**Rationale:** Universal AA mapping; Portal has limited SPAAG options.

---

#### Quadbike (Quad ATV) - 6 mappings

**Light Reconnaissance Vehicles** - Used for all WW2 jeeps/cars.

```
American:
- Willys, WillysMB, Jeep (Willys MB)

German:
- Kubelwagen (Volkswagen Kübelwagen)

Soviet:
- GAZ, GAZ67 (GAZ-67)
```

**Rationale:** Fast, lightly armored transport role preserved.

---

#### CV90 (Combat Vehicle 90) - 4 mappings

**German Tank Destroyers** - Used for assault guns and SPGs.

```
German:
- StuG, StuG3, StuGIII (StuG III assault gun)
- Wespe (Wespe self-propelled howitzer)
```

**Rationale:** Infantry support vehicle → modern IFV with cannon.

---

#### Flyer60 (Hovercraft) - 4 mappings

**Amphibious & Naval Transport** - Used for landing craft.

```
American:
- LandingCraft, LCVP, Higgins (Higgins boat)
- DUKW (DUKW amphibious truck)
```

**Rationale:** Water/land transport role; Portal lacks dedicated landing craft.

---

#### Vector (Transport APC) - 4 mappings

**Armored Personnel Carriers** - Used for halftracks.

```
German:
- Hanomag (Sd.Kfz. 251)

American:
- M3, M3A1, Halftrack (M3 Half-track)
```

**Rationale:** Armored troop transport → modern wheeled APC.

---

#### Cheetah (Light Vehicle) - 3 mappings

**Japanese Light Tanks** - Used for undergunned/lightly armored tanks.

```
Japanese:
- TypeChiHa, Chi-Ha, Type97 (Type 97 Chi-Ha)
```

**Rationale:** Light tank performance → modern light reconnaissance vehicle.

---

#### Eurocopter (Tiger Attack Helicopter) - 3 mappings

**Axis Ground Attack** - Used for German dive bombers.

```
German:
- Ju87, Stuka (Junkers Ju 87)
- Ju88 (Junkers Ju 88)
```

**Rationale:** Ground attack role preserved; Axis → non-NATO attack helicopter.

---

#### JAS39 (Saab JAS 39 Gripen) - 3 mappings

**Allied Strategic Bombers** - Used for heavy bombers.

```
American:
- B17, B-17 (B-17 Flying Fortress)

British:
- Lancaster (Avro Lancaster)
```

**Rationale:** Multirole fighter with ground attack capability.

---

#### UH60 (UH-60 Black Hawk) - 3 mappings

**Transport Helicopters** - Modern additions (not in original BF1942).

```
Modern (custom):
- TransportHeli, BlackHawk, UH60
```

**Rationale:** Enables modern combined arms gameplay.

---

#### M2Bradley (M2 Bradley IFV) - 2 mappings

**American Self-Propelled Artillery** - Used for SPGs.

```
American:
- Priest, M7Priest (M7 Priest)
```

**Rationale:** Infantry support vehicle with indirect fire capability.

---

#### F22 (F-22 Raptor) - 0 mappings

**UNUSED** - Reserved for future high-performance aircraft.

**Potential Use Cases:**
- Jet-era maps (Korea, Vietnam, Gulf War)
- Special "super-fighter" spawns
- Asymmetric air superiority scenarios

---

## Mappings by Category

### Tank (25 mappings)

**German (Axis) → Leopard:**
- Panzer4, PanzerIV, PanzerV, Panther, PanzerVI, Tiger, TigerTank

**American (Allied) → Abrams:**
- Sherman, ShermanTank, M4Sherman, M4A3, M10, M10Wolverine

**Soviet (Allied) → Abrams:**
- T34, T-34, T3485, T-34-85, KV1, KV-1

**British (Allied) → Abrams:**
- Churchill, ChurchillTank, Crusader

**Japanese (Axis) → Cheetah:**
- TypeChiHa, Chi-Ha, Type97

---

### Fighter (14 mappings)

**Axis → SU57:**
- BF109, Bf109, Me109, Messerschmitt, FW190, Focke-Wulf (German)
- Zero, A6M (Japanese)

**Allied → F16:**
- P51, P-51, Mustang (American)
- Spitfire (British)
- Yak9, Yak-9 (Soviet)

---

### Dive Bomber (7 mappings)

**Axis → Eurocopter:**
- Ju87, Stuka, Ju88 (German)

**Allied → AH64:**
- IL2, IL-2, Ilyushin, Sturmovik (Soviet)

---

### Anti-Air (6 mappings → Gepard)

- Flak38, Flak36, Flak88, WirbelWind (German)
- M16, M16AAA (American)

---

### Light Vehicle (6 mappings → Quadbike)

- Willys, WillysMB, Jeep (American)
- Kubelwagen (German)
- GAZ, GAZ67 (Soviet)

---

### APC (4 mappings → Vector)

- Hanomag (German)
- M3, M3A1, Halftrack (American)

---

### Naval (4 mappings → Flyer60)

- LandingCraft, LCVP, Higgins, DUKW (American)

---

### Tank Destroyer (4 mappings → CV90)

- StuG, StuG3, StuGIII, Wespe (German)

---

### Bomber (3 mappings → JAS39)

- B17, B-17 (American)
- Lancaster (British)

---

### Attack Helicopter (3 mappings → AH64)

- AttackHeli, Apache, AH64 (Modern, not in BF1942)

---

### Transport Helicopter (3 mappings → UH60)

- TransportHeli, BlackHawk, UH60 (Modern, not in BF1942)

---

### SPG (2 mappings → M2Bradley)

- Priest, M7Priest (American)

---

## Special Cases & Notes

### 1. Japanese Light Tanks → Cheetah

**Why not Leopard/Abrams?**

The Type 97 Chi-Ha was significantly undergunned compared to German/Allied medium tanks:
- **Chi-Ha:** 57mm gun, 25mm armor
- **Sherman:** 75mm gun, 76mm armor
- **Panzer IV:** 75mm gun, 80mm armor

**Solution:** Map to Cheetah (light vehicle) to preserve performance characteristics.

---

### 2. Dive Bombers → Attack Helicopters

**Historical Role:** Close air support and ground attack

**Modern Equivalent:** Attack helicopters fulfill the same battlefield role

**Faction Alignment:**
- **German Ju-87 Stuka** → Eurocopter Tiger (non-NATO)
- **Soviet Il-2 Sturmovik** → AH-64 Apache (NATO)

---

### 3. Strategic Bombers → Multirole Fighters

**Challenge:** Portal has no strategic bomber class

**Solution:** Map to JAS39 Gripen (multirole fighter with ground attack)

- B-17 Flying Fortress → JAS39
- Lancaster → JAS39

**Rationale:** Preserves air-to-ground strike capability in modern context.

---

### 4. Naval Vessels

**BF1942 Naval Assets NOT Mapped:**
- Battleships (USS Enterprise, IJN Yamato)
- Destroyers (Fletcher-class, Fubuki-class)
- Submarines (Gato-class, Type VII U-boat)
- PT Boats

**Portal Limitation:** No capital ships or complex naval combat

**Workaround:** Landing craft map to Flyer60 hovercraft for amphibious assault.

---

### 5. Stationary Weapons

**NOT in VehicleMapper:**
- Fixed AA guns (Flak 38, Bofors 40mm)
- Fixed MGs (MG42, Browning M2)
- Coastal artillery
- Anti-tank guns

**Handled By:** Separate static weapon system in Portal SDK

---

### 6. Variants & Naming Inconsistencies

**BF1942 used inconsistent naming across maps:**

| Canonical Name | Variants in Mappings |
|----------------|----------------------|
| Bf 109 | BF109, Bf109, Me109, Messerschmitt |
| T-34 | T34, T-34, T3485, T-34-85 |
| M4 Sherman | Sherman, ShermanTank, M4Sherman, M4A3 |
| StuG III | StuG, StuG3, StuGIII |

**Solution:** All variants map to same BF6 VehicleType.

---

### 7. Expansion Pack Vehicles

**Road to Rome (XPack1):**
- Italian vehicles (mostly stationary weapons, no unique mobiles)

**Secret Weapons of WWII (XPack2):**
- Experimental vehicles (not yet mapped):
  - Wasserfall rocket
  - Horsa glider
  - Goblin jetpack

**Status:** Expansion vehicles require manual review and custom mappings.

---

### 8. Modern Vehicles (Custom Additions)

These are **NOT** in original BF1942, but added for modern gameplay:

- AttackHeli, Apache, AH64 → AH64
- TransportHeli, BlackHawk, UH60 → UH60

**Use Case:** Custom maps mixing WW2 and modern eras.

---

## Usage Examples

### Example 1: Basic Vehicle Mapping

```python
from tools.bfportal.mappers.vehicle_mapper import VehicleMapper

mapper = VehicleMapper()

# Map a German tank
bf6_type = mapper.map_vehicle("PanzerIV")
print(bf6_type)  # Output: "Leopard"

# Map an American tank
bf6_type = mapper.map_vehicle("Sherman")
print(bf6_type)  # Output: "Abrams"

# Get detailed info
info = mapper.get_mapping_info("Stuka")
print(info.category)      # Output: "Dive Bomber"
print(info.bf6_vehicle_type)  # Output: "Eurocopter"
print(info.notes)         # Output: "Axis dive bomber → Eurocopter Tiger (non-NATO)"
```

---

### Example 2: Faction-Aware Mapping

```python
# Original BF1942 spawner from .con file
# ObjectTemplate.create ObjectSpawner PanzerIVSpawner
# ObjectTemplate.setObjectTemplate 1 PanzerIV
# ObjectTemplate.team 1  # Axis team

# After conversion:
vehicle_type = mapper.map_vehicle("PanzerIV")  # Returns "Leopard"
bf6_team = 2  # Axis → Team 2 (non-NATO)

# Generated .tscn node:
# [node name="PanzerIVSpawner" parent="." instance=ExtResource("VehicleSpawner")]
# VehicleType = "Leopard"
# Team = 2
```

---

### Example 3: Category-Based Queries

```python
# Get all tank mappings
tank_mappings = mapper.get_mappings_by_category("Tank")
print(f"Total tanks: {len(tank_mappings)}")  # 25

# Get all aircraft
fighters = mapper.get_mappings_by_category("Fighter")
bombers = mapper.get_mappings_by_category("Dive Bomber")
aircraft = {**fighters, **bombers}
print(f"Total aircraft: {len(aircraft)}")  # 21
```

---

### Example 4: Coverage Analysis

```python
# Check which BF6 types are used
bf6_types = mapper.get_bf6_vehicle_types()
print(f"Using {len(bf6_types)}/16 available types")  # 15/16

# Available but unused
all_types = ["Abrams", "Leopard", "Cheetah", "CV90", "Gepard",
             "UH60", "Eurocopter", "AH64", "Vector", "Quadbike",
             "Flyer60", "JAS39", "F22", "F16", "M2Bradley", "SU57"]
unused = set(all_types) - set(bf6_types)
print(f"Unused types: {unused}")  # {'F22'}
```

---

### Example 5: Handling Unmapped Vehicles

```python
# Unknown vehicle
result = mapper.map_vehicle("MausSupertank")
if result is None:
    print("Vehicle not mapped, using fallback logic")
    # Fall back to category-based heuristics
    # or skip vehicle entirely
```

---

## Maps Analyzed (36 Total)

### Base Game (16 maps)
- Battle_of_Britain, Battle_of_the_Bulge, Battleaxe
- Berlin, Bocage, El_Alamein, Gazala
- Guadalcanal, Iwo_Jima, Kharkov, Kursk
- Market_Garden, Midway, Omaha_Beach
- Stalingrad, Tobruk, Wake

### Road to Rome (8 maps)
- Anzio, Baytown, Husky, Monte_Cassino
- Operation_Husky, Salerno, Tobruk_043, Tunis

### Secret Weapons (12 maps)
- Coral_Sea, Essen, Factory, Gazala_SW
- Invasion_of_the_Philippines, Liberation_of_Caen
- Raid_on_Agheila, Rails_and_Metal, Telemark
- The_Battle_of_Britain_SW, Tundra, V2_Rocket

---

## Manual Review Needed

### Expansion Pack Vehicles (Secret Weapons)

**Experimental Aircraft:**
- Horsa Glider → ? (no equivalent)
- Arado Ar 234 (jet bomber) → JAS39 or F16?

**Experimental Ground:**
- Wasserfall SAM → Gepard?
- Goblin jetpack → (no equivalent, skip?)

**Recommendation:** Review individual .con files for accurate classification.

---

### Custom/Modded Maps

If converting community-made BF1942 maps:
1. Check for custom vehicle types
2. Use `VehicleMapper.map_vehicle()` for lookup
3. If `None` returned, manually categorize
4. Add to local mapping override file

---

## Validation Checklist

When converting a BF1942 map, verify:

- [ ] All vehicles have BF6 VehicleType mapping
- [ ] Axis vehicles use non-NATO types (Leopard, SU57, Eurocopter)
- [ ] Allied vehicles use NATO types (Abrams, F16, AH64)
- [ ] Teams are swapped (BF1942 Team 1 → BF6 Team 2)
- [ ] Vehicle spawn positions preserved
- [ ] Vehicle rotation/orientation correct
- [ ] No unmapped vehicles in .con files

---

## Future Enhancements

### Potential Additions

1. **BF Vietnam vehicles** (UH-1 Huey, M113, T-55)
2. **BF2 vehicles** (M1A2, T-90, F-18)
3. **BF2142 vehicles** (walkers, hover tanks)
4. **Expansion pack experimental weapons**

### Configuration Options

Consider adding:
- Map-specific vehicle overrides
- Era-based filtering (WW2-only mode)
- Faction rebalancing options
- Custom vehicle definitions

---

## Related Documentation

- **VehicleSpawner.gd:** Portal SDK vehicle spawner node definition
- **vehicle_mapper.py:** Source code implementation
- **portal_vehicle_report.py:** Generates mapping statistics
- **CLAUDE.md:** Project overview and conventions
- **BF1942_ASSET_MAPPINGS.md:** Complete asset mapping reference (all categories)

---

## Credits

**Project:** BF1942 to BF6 Portal SDK Conversion
**Author:** Zach Atkinson
**AI Assistant:** Claude (Anthropic)
**License:** [Project License]

---

**End of Document**
