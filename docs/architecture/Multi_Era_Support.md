# Multi-Era Support Strategy

**Date:** 2025-10-11
**Purpose:** Future-proof the conversion pipeline for multiple time periods

---

## Overview

The BF1942 → BF6 conversion pipeline is **designed to support multiple eras** if EA/DICE expands Portal with classic assets.

**Current Status:** Using modern BF6 assets (Leopard, Abrams, F-16, etc.)
**Future Possibility:** WW2, Vietnam, Cold War asset packs

**Our system is ready for this!** 🎯

---

## Architecture: Era-Agnostic Design

### Data Layer (Permanent)

**`tools/kursk_extracted_data.json`**
- Contains ORIGINAL BF1942 positions
- Time period agnostic
- Never needs updating for new eras
- Same data works for ALL time periods

**Example:**
```json
{
  "vehicle_spawners": [{
    "bf1942_type": "lighttankspawner",
    "position": {"x": 450.345, "y": 78.6349, "z": 249.093},
    "rotation": {"pitch": 0.0, "yaw": 0.103998, "roll": 1.52588},
    "team": 1
  }]
}
```

**This position is PERMANENT.** It works for:
- ✅ Modern Leopard tank
- ✅ WW2 Panzer IV (if added)
- ✅ Vietnam M48 Patton (if added)
- ✅ Any future tank asset

### Mapping Layer (Swappable)

**`tools/object_mapping_database.json`**
- THE ONLY FILE THAT CHANGES for new eras
- Maps BF1942 objects → BF6 assets
- Easy to duplicate for different time periods

**Current (Modern):**
```json
{
  "vehicle_spawners": {
    "lighttankspawner": {
      "bf6_vehicle_template_axis": "VEH_Leopard",
      "bf6_vehicle_template_allies": "VEH_Abrams"
    }
  }
}
```

**Future (WW2 - when available):**
```json
{
  "vehicle_spawners": {
    "lighttankspawner": {
      "bf6_vehicle_template_axis": "VEH_Panzer_IV_1942",
      "bf6_vehicle_template_allies": "VEH_Sherman_1942"
    }
  }
}
```

### Generation Layer (Automated)

**`tools/generate_kursk_tscn.py`**
- Reads extracted data
- Reads mapping database
- Generates .tscn
- Now supports custom mappings!

**Usage:**
```bash
# Modern Kursk (default)
python tools/generate_kursk_tscn.py

# WW2 Kursk (when assets available)
python tools/generate_kursk_tscn.py \
  --mapping tools/object_mapping_database_ww2.json \
  --output GodotProject/levels/Kursk_WW2.tscn
```

---

## Multi-Era Workflow

### When EA Releases WW2 Asset Pack

**Step 1: Catalog New Assets**

Run asset analysis on updated SDK:
```bash
python tools/analyze_bf6_assets.py
```

Identify WW2 vehicles:
- VEH_Panzer_IV_1942
- VEH_Sherman_1942
- VEH_Bf109_1942
- VEH_Stuka_1942
- etc.

**Step 2: Create WW2 Mapping Database**

Copy and modify:
```bash
cp tools/object_mapping_database.json \
   tools/object_mapping_database_ww2.json
```

Edit mappings:
```json
{
  "metadata": {
    "version": "1.0.0-ww2",
    "description": "WW2-era asset mappings for Kursk",
    "era": "World War 2 (1942)"
  },
  "vehicle_spawners": {
    "lighttankspawner": {
      "bf6_vehicle_template_axis": "VEH_Panzer_IV_1942",
      "bf6_vehicle_template_allies": "VEH_Sherman_1942",
      "notes": "Authentic WW2 light tanks"
    },
    "heavytankspawner": {
      "bf6_vehicle_template_axis": "VEH_Tiger_I_1942",
      "bf6_vehicle_template_allies": "VEH_M4A3E8_1942",
      "notes": "Authentic WW2 heavy tanks"
    },
    "FighterSpawner": {
      "bf6_vehicle_template": "VEH_Bf109_1942",
      "notes": "WW2 fighter aircraft"
    },
    "DiveBomberSpawner": {
      "bf6_vehicle_template": "VEH_Stuka_1942",
      "notes": "WW2 dive bomber"
    }
  },
  "terrain": {
    "bf6_terrain": {
      "selected_map": "MP_BattleOfTheBulge_Terrain",
      "rationale": "WW2-era terrain with appropriate vegetation"
    }
  }
}
```

**Step 3: Generate WW2 Version**

```bash
python tools/generate_kursk_tscn.py \
  --mapping tools/object_mapping_database_ww2.json \
  --output GodotProject/levels/Kursk_WW2.tscn
```

**Step 4: Test in Godot**

Open `Kursk_WW2.tscn` - should have WW2 assets at SAME positions!

---

## Multiple Era Variants

### Maintain Parallel Versions

**Directory Structure:**
```
tools/
├── kursk_extracted_data.json              # SOURCE DATA (permanent)
├── object_mapping_database.json           # Modern (current)
├── object_mapping_database_ww2.json       # WW2 (future)
├── object_mapping_database_vietnam.json   # Vietnam (future)
├── object_mapping_database_coldwar.json   # Cold War (future)

GodotProject/levels/
├── Kursk.tscn                             # Modern version
├── Kursk_WW2.tscn                         # WW2 version (future)
├── Kursk_Vietnam.tscn                     # Vietnam version (future)
├── Kursk_ColdWar.tscn                     # Cold War version (future)
```

### Generate All Variants

**Batch script:**
```bash
#!/bin/bash
# Generate all era variants of Kursk

echo "Generating Kursk variants..."

# Modern (default)
python tools/generate_kursk_tscn.py

# WW2 (if assets available)
if [ -f "tools/object_mapping_database_ww2.json" ]; then
  python tools/generate_kursk_tscn.py \
    --mapping tools/object_mapping_database_ww2.json \
    --output GodotProject/levels/Kursk_WW2.tscn
fi

# Vietnam (if assets available)
if [ -f "tools/object_mapping_database_vietnam.json" ]; then
  python tools/generate_kursk_tscn.py \
    --mapping tools/object_mapping_database_vietnam.json \
    --output GodotProject/levels/Kursk_Vietnam.tscn
fi

echo "✅ All variants generated!"
```

---

## Era-Specific Considerations

### Vehicle Mappings

**Modern Era:**
- Leopard 2 (Germany) / Abrams (USA)
- F-16 fighters
- AH-64 Apache helicopters

**WW2 Era:**
- Panzer IV / Sherman
- Bf 109 / P-51 Mustang fighters
- Stuka / Dauntless dive bombers

**Vietnam Era:**
- M48 Patton / T-54 tanks
- F-4 Phantom / MiG-21 fighters
- UH-1 Huey helicopters

**Cold War Era:**
- M60 / T-72 tanks
- F-15 / MiG-29 fighters
- AH-1 Cobra helicopters

### Terrain Considerations

Each era might have different terrain assets:

**Modern:**
- MP_Outskirts (current choice)
- Clean, modern infrastructure

**WW2:**
- MP_BattleOfTheBulge_Terrain (if available)
- Period-appropriate buildings
- WW2 bunkers and fortifications

**Vietnam:**
- Jungle terrain
- Rice paddies
- Village structures

**Cold War:**
- Industrial facilities
- Military installations
- Urban environments

---

## Refactoring Checklist

When new era assets become available:

### Phase 1: Asset Discovery
- [ ] Run `analyze_bf6_assets.py` on updated SDK
- [ ] Identify new vehicle types
- [ ] Identify new terrain options
- [ ] Document asset restrictions

### Phase 2: Mapping Creation
- [ ] Copy existing mapping database
- [ ] Rename for new era (e.g., `_ww2.json`)
- [ ] Update vehicle mappings
- [ ] Update terrain selection
- [ ] Update metadata

### Phase 3: Generation
- [ ] Run generator with new mapping
- [ ] Specify custom output path
- [ ] Validate generated .tscn
- [ ] Check for missing resources

### Phase 4: Testing
- [ ] Open in Godot
- [ ] Verify asset placements
- [ ] Check visual consistency
- [ ] Test gameplay balance
- [ ] Export to .spatial.json

### Phase 5: Documentation
- [ ] Update README with new era support
- [ ] Document asset choices
- [ ] Note any compromises
- [ ] Update Phase 3 documentation

---

## Code Changes Needed: ZERO

**The generator already supports this!**

Enhanced in Phase 3 with command-line arguments:
- `--mapping <path>` - Use custom mapping database
- `--output <path>` - Generate to custom location

**No code changes needed for new eras!**

---

## Benefits of This Design

### 1. **Future-Proof**
- Works with ANY future asset pack
- No code rewrite needed
- Just swap mapping files

### 2. **Data Preservation**
- Original BF1942 positions preserved
- Can regenerate anytime
- Source data never modified

### 3. **Easy Experimentation**
- Try different asset combinations
- Test multiple eras
- Quick iteration

### 4. **Maintainable**
- Clear separation of concerns
- Single file to update per era
- Well-documented process

### 5. **Scalable**
- Works for all BF1942 maps
- Not just Kursk
- Pipeline proven and reusable

---

## Example: Adding Vietnam Era

**Hypothetical Vietnam Asset Pack Released**

**1. Create mapping:**
```bash
cp tools/object_mapping_database.json \
   tools/object_mapping_database_vietnam.json
```

**2. Edit for Vietnam vehicles:**
```json
{
  "vehicle_spawners": {
    "lighttankspawner": {
      "bf6_vehicle_template": "VEH_M48_Patton_Vietnam"
    },
    "FighterSpawner": {
      "bf6_vehicle_template": "VEH_F4_Phantom_Vietnam"
    },
    "DiveBomberSpawner": {
      "bf6_vehicle_template": "VEH_UH1_Huey_Vietnam"
    }
  },
  "terrain": {
    "selected_map": "MP_Vietnam_Jungle"
  }
}
```

**3. Generate:**
```bash
python tools/generate_kursk_tscn.py \
  --mapping tools/object_mapping_database_vietnam.json \
  --output GodotProject/levels/Kursk_Vietnam.tscn
```

**4. Test:**
- Open in Godot
- See Vietnam-era vehicles at Kursk positions
- Jungle terrain instead of plains

**Time Required: 30 minutes**

---

## Comparison: Our System vs Manual

### Manual Recreation (Traditional Approach)

**Per Era:**
- ⏱️ 10+ hours: Place all objects manually
- 🐛 Error-prone: Manual positioning
- 📝 No automation: Repeat for each map
- 🔄 Hard to update: Redo everything

**Total for 3 eras:** 30+ hours

### Our Automated System

**Per Era:**
- ⏱️ 10 minutes: Update mapping file
- ⏱️ 5 seconds: Run generator
- ✅ Consistent: Same positions every time
- 🔄 Easy updates: Regenerate anytime

**Total for 3 eras:** 30 minutes

**100x faster!** 🚀

---

## When Will This Matter?

### Scenarios Where Multi-Era Support Shines

**1. EA Releases Classic Asset Pack**
- WW2 vehicles added to BF6 Portal
- Community wants authentic remakes
- Our system: instant WW2 Kursk

**2. Community Modding Opens Up**
- Custom asset imports allowed
- Modders create period vehicles
- Our system: plug-and-play support

**3. Multiple Map Conversions**
- Convert all 16 BF1942 maps
- Each in multiple eras
- 16 maps × 3 eras = 48 variants
- Automated: ~8 hours total
- Manual: ~480 hours

**4. Gameplay Balance Testing**
- Test same layout with different vehicles
- Compare eras for balance
- Rapid iteration

---

## Recommendation

### Now
- ✅ Use modern assets (what's available)
- ✅ System is already future-proof
- ✅ Continue with Phase 4 testing

### When WW2 Assets Available
- ✏️ Create `object_mapping_database_ww2.json`
- ▶️ Run generator with `--mapping` flag
- 🎮 Get WW2 Kursk instantly

### If Converting More Maps
- 🗺️ Apply same pipeline to El Alamein, Wake Island, etc.
- 📦 Build library of mapping databases
- 🔄 Generate all variants on demand

---

## Summary

**Q: Can we refactor for different time periods later?**
**A: ABSOLUTELY YES!** ✅

**Our system is designed for this:**
- Data layer: Permanent, era-agnostic
- Mapping layer: Swappable per era
- Generation layer: Automated, supports custom mappings

**To support new era:**
1. Create new mapping JSON (~10 min)
2. Run generator with `--mapping` flag (5 sec)
3. Done!

**No code changes needed. Already implemented!** 🎯

---

*Last Updated:* 2025-10-11
*Status:* Ready for multi-era support
*Next Action:* Wait for EA to release classic assets... or continue with modern version!
