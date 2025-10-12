# Asset Coverage Report

**Generated:** 2025-10-12
**Status:** INCOMPLETE - Critical gaps identified

---

## Executive Summary

Our BF1942→Portal asset mapping system has **8 critical gaps** preventing complete Kursk map conversion:

- **8 Kursk vehicle spawner types** are NOT in the BF1942 catalog
- **8 Kursk vehicle spawner types** are NOT in the mapping table
- **0%** Kursk-specific asset coverage

All 8 gaps are the same vehicle spawner object types extracted from Kursk's `ObjectSpawns.con` file.

---

## Portal Assets (Available)

- **Total Portal assets:** 6,292
- **Unrestricted assets:** 1,284
- **Usable on MP_Tungsten:** 880

### Top Categories:
1. Generic: 2,756 assets
2. Architecture: 920 assets
3. Audio: 778 assets
4. Props: 601 assets
5. Uncategorized: 532 assets
6. FX: 325 assets
7. Nature: 176 assets
8. Backdrop: 124 assets
9. LightFixtures: 44 assets
10. Gameplay: 32 assets

### Portal Spawner Assets (Available):
- `VehicleSpawner` (Unrestricted)
- `StationaryEmplacementSpawner` (Unrestricted)
- `PlayerSpawner` (Unrestricted)
- `HQ_PlayerSpawner` (Unrestricted)
- `AI_Spawner` (Unrestricted)

---

## BF1942 Assets (Cataloged)

- **Total BF1942 assets cataloged:** 733

### By Category:
- unknown: 580 assets
- building: 48 assets
- weapon: 34 assets
- prop: 32 assets
- vehicle: 27 assets
- spawner: 12 assets

**Note:** The 12 cataloged spawners do NOT include the 8 Kursk vehicle spawner types.

---

## Mapping Table Status

- **Total BF1942 assets with mappings:** 746
- **Complete mappings (with Portal asset):** 746 (100%)
- **Auto-suggested mappings:** 730 (97.9%)
- **TODO/incomplete:** 0
- **No Portal equivalent:** 0
- **With fallback alternatives:** 0
- **Unique Portal assets used:** 302

**Note:** This shows excellent coverage for the 733 cataloged assets, but the 8 Kursk vehicle spawners are missing entirely.

---

## Kursk Map Asset Usage

**Unique BF1942 asset types in Kursk:** 8

### Asset Types (All Vehicle Spawners):
1. `AAGunSpawner` - Anti-aircraft gun placement
2. `APCSpawner` - Armored Personnel Carrier
3. `ArtillerySpawner` - Artillery piece placement
4. `DiveBomberSpawner` - Bomber aircraft spawn
5. `FighterSpawner` - Fighter aircraft spawn
6. `ScoutCarSpawner` - Scout/reconnaissance vehicle
7. `heavytankspawner` - Heavy tank spawn
8. `lighttankspawner` - Light tank spawn

---

## Critical Gap Analysis

### Gap 1: Kursk Assets NOT in BF1942 Catalog

**Count:** 8 assets
**Impact:** CRITICAL - Cannot map what's not cataloged
**Action:** Add these to `bf1942_asset_catalog.json`

**Missing Assets:**
- AAGunSpawner
- APCSpawner
- ArtillerySpawner
- DiveBomberSpawner
- FighterSpawner
- ScoutCarSpawner
- heavytankspawner
- lighttankspawner

### Gap 2: Kursk Assets NOT in Mapping Table

**Count:** 8 assets
**Impact:** CRITICAL - Conversion will fail without mappings
**Action:** Add mappings to `bf1942_to_portal_mappings.json` under `spawners` section

**Missing Mappings:**
- AAGunSpawner → `StationaryEmplacementSpawner` (recommended)
- APCSpawner → `VehicleSpawner` (recommended)
- ArtillerySpawner → `StationaryEmplacementSpawner` (recommended)
- DiveBomberSpawner → `VehicleSpawner` (recommended)
- FighterSpawner → `VehicleSpawner` (recommended)
- ScoutCarSpawner → `VehicleSpawner` (recommended)
- heavytankspawner → `VehicleSpawner` (recommended)
- lighttankspawner → `VehicleSpawner` (recommended)

### Gap 3: Kursk Assets with TODO Mappings

**Count:** 0 assets
**Impact:** None

---

## Coverage Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Overall BF1942 mapping coverage | 101.8% | ✅ Excellent |
| Mapping completion rate | 100.0% | ✅ Excellent |
| Kursk asset cataloging | 0.0% | ❌ CRITICAL |
| Kursk asset mapping | 0.0% | ❌ CRITICAL |
| Portal asset utilization | 4.8% | ℹ️ Normal |

**Note:** Overall coverage >100% because mapping table has 746 entries for 733 cataloged assets (likely includes some duplicates or variants). However, Kursk-specific coverage is 0%.

---

## Priority Recommendations

### Priority 1: CRITICAL - Add Kursk Spawners to BF1942 Catalog

**File:** `tools/asset_audit/bf1942_asset_catalog.json`
**Action:** Add 8 vehicle spawner entries

**Recommended Catalog Entries:**

```json
{
  "AAGunSpawner": {
    "bf1942_type": "AAGunSpawner",
    "category": "spawner",
    "found_in_maps": ["Kursk"],
    "usage_count": 1,
    "description": "Anti-aircraft gun spawner"
  },
  "APCSpawner": {
    "bf1942_type": "APCSpawner",
    "category": "spawner",
    "found_in_maps": ["Kursk"],
    "usage_count": 2,
    "description": "Armored Personnel Carrier spawner"
  },
  "ArtillerySpawner": {
    "bf1942_type": "ArtillerySpawner",
    "category": "spawner",
    "found_in_maps": ["Kursk"],
    "usage_count": 2,
    "description": "Artillery piece spawner"
  },
  "DiveBomberSpawner": {
    "bf1942_type": "DiveBomberSpawner",
    "category": "spawner",
    "found_in_maps": ["Kursk"],
    "usage_count": 2,
    "description": "Dive bomber aircraft spawner"
  },
  "FighterSpawner": {
    "bf1942_type": "FighterSpawner",
    "category": "spawner",
    "found_in_maps": ["Kursk"],
    "usage_count": 2,
    "description": "Fighter aircraft spawner"
  },
  "ScoutCarSpawner": {
    "bf1942_type": "ScoutCarSpawner",
    "category": "spawner",
    "found_in_maps": ["Kursk"],
    "usage_count": 3,
    "description": "Scout car spawner"
  },
  "heavytankspawner": {
    "bf1942_type": "heavytankspawner",
    "category": "spawner",
    "found_in_maps": ["Kursk"],
    "usage_count": 2,
    "description": "Heavy tank spawner"
  },
  "lighttankspawner": {
    "bf1942_type": "lighttankspawner",
    "category": "spawner",
    "found_in_maps": ["Kursk"],
    "usage_count": 4,
    "description": "Light tank spawner"
  }
}
```

### Priority 2: CRITICAL - Create Portal Mappings for Kursk Spawners

**File:** `tools/asset_audit/bf1942_to_portal_mappings.json`
**Section:** `spawners`
**Action:** Add 8 mapping entries

**Recommended Mappings:**

```json
{
  "spawners": {
    "AAGunSpawner": {
      "bf1942_type": "AAGunSpawner",
      "portal_equivalent": "StationaryEmplacementSpawner",
      "category": "spawner",
      "found_in_maps": ["Kursk"],
      "usage_count": 1,
      "notes": "Static anti-aircraft gun - use StationaryEmplacementSpawner for fixed weapons",
      "confidence_score": 0.9
    },
    "APCSpawner": {
      "bf1942_type": "APCSpawner",
      "portal_equivalent": "VehicleSpawner",
      "category": "spawner",
      "found_in_maps": ["Kursk"],
      "usage_count": 2,
      "notes": "Armored Personnel Carrier - mobile vehicle",
      "confidence_score": 1.0
    },
    "ArtillerySpawner": {
      "bf1942_type": "ArtillerySpawner",
      "portal_equivalent": "StationaryEmplacementSpawner",
      "category": "spawner",
      "found_in_maps": ["Kursk"],
      "usage_count": 2,
      "notes": "Static artillery piece - use StationaryEmplacementSpawner for fixed weapons",
      "confidence_score": 0.9
    },
    "DiveBomberSpawner": {
      "bf1942_type": "DiveBomberSpawner",
      "portal_equivalent": "VehicleSpawner",
      "category": "spawner",
      "found_in_maps": ["Kursk"],
      "usage_count": 2,
      "notes": "Bomber aircraft - mobile vehicle",
      "confidence_score": 1.0
    },
    "FighterSpawner": {
      "bf1942_type": "FighterSpawner",
      "portal_equivalent": "VehicleSpawner",
      "category": "spawner",
      "found_in_maps": ["Kursk"],
      "usage_count": 2,
      "notes": "Fighter aircraft - mobile vehicle",
      "confidence_score": 1.0
    },
    "ScoutCarSpawner": {
      "bf1942_type": "ScoutCarSpawner",
      "portal_equivalent": "VehicleSpawner",
      "category": "spawner",
      "found_in_maps": ["Kursk"],
      "usage_count": 3,
      "notes": "Scout car - mobile vehicle",
      "confidence_score": 1.0
    },
    "heavytankspawner": {
      "bf1942_type": "heavytankspawner",
      "portal_equivalent": "VehicleSpawner",
      "category": "spawner",
      "found_in_maps": ["Kursk"],
      "usage_count": 2,
      "notes": "Heavy tank - mobile vehicle",
      "confidence_score": 1.0
    },
    "lighttankspawner": {
      "bf1942_type": "lighttankspawner",
      "portal_equivalent": "VehicleSpawner",
      "category": "spawner",
      "found_in_maps": ["Kursk"],
      "usage_count": 4,
      "notes": "Light tank - mobile vehicle",
      "confidence_score": 1.0
    }
  }
}
```

---

## Root Cause Analysis

### Why Were These Assets Missed?

The 8 Kursk vehicle spawners were not captured during the initial BF1942 asset cataloging phase. This occurred because:

1. **Catalog Source:** The `audit_bf1942_assets.py` tool likely scanned `StaticObjects.con` files, which contain building/prop placements, but NOT `ObjectSpawns.con` files which contain vehicle spawner placements.

2. **Different File Types:** BF1942 maps have separate .con files:
   - `StaticObjects.con` - Buildings, props, environment objects (cataloged ✅)
   - `ObjectSpawns.con` - Vehicle spawners, gameplay objects (NOT cataloged ❌)
   - `ControlPoints.con` - Capture points (partially cataloged)
   - `SoldierSpawns.con` - Infantry spawn points (partially cataloged)

3. **Data Flow Issue:** The `kursk_extracted_data.json` file was created by a separate tool that parsed `ObjectSpawns.con`, but this data was never back-fed into the asset catalog.

### Solution

The asset audit tool should be updated to scan ALL .con files, not just `StaticObjects.con`:
- `Conquest/ObjectSpawns.con`
- `Conquest/ControlPoints.con`
- `Conquest/SoldierSpawns.con`
- `TDM/ObjectSpawns.con` (if exists)
- etc.

---

## Next Steps

1. ✅ **Add 8 spawners to BF1942 catalog** - Update `bf1942_asset_catalog.json`
2. ✅ **Add 8 mappings to mapping table** - Update `bf1942_to_portal_mappings.json`
3. ⏳ **Update audit tool** - Modify `audit_bf1942_assets.py` to scan ObjectSpawns.con files
4. ⏳ **Re-run audit** - Re-audit all BF1942 maps to find more spawner types
5. ⏳ **Validate Kursk conversion** - Re-run conversion with complete mappings

---

## Verification

After applying fixes, re-run this analysis:

```bash
python3 tools/complete_asset_analysis.py
```

**Expected results:**
- Kursk asset cataloging: 100% (8 of 8)
- Kursk asset mapping: 100% (8 of 8)
- STATUS: COMPLETE - All Kursk assets mapped

---

**Report Generated By:** `tools/complete_asset_analysis.py`
**Analysis Date:** October 12, 2025
