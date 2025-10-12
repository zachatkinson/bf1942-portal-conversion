# CLI Tools Reference

> Complete command-line tool documentation for converting Battlefield maps to Portal format

**Purpose:** Comprehensive reference for all command-line conversion tools, options, and workflows
**Last Updated:** October 2025
**Status:** Production Ready

---

## Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Available Tools](#available-tools)
  - [portal_convert.py](#portal_convertpy---master-cli)
  - [portal_parse.py](#portal_parsepy---parser-only)
  - [portal_map_assets.py](#portal_map_assetspy---asset-mapper)
  - [portal_adjust_heights.py](#portal_adjust_heightspy---height-adjuster)
  - [portal_rebase.py](#portal_rebasepy---terrain-switcher)
  - [portal_generate.py](#portal_generatepy---scene-generator)
  - [portal_validate.py](#portal_validatepy---validator)
- [Configuration Files](#configuration-files)
- [Workflows](#workflows)
- [Troubleshooting](#troubleshooting)
- [Architecture](#architecture)

---

## Quick Start

### Convert a BF1942 Map

```bash
python3 tools/portal_convert.py --map Kursk --base-terrain MP_Tungsten
```

**This will:**
1. Parse BF1942 Kursk map files
2. Map 733 assets to Portal equivalents
3. Calculate coordinate offsets
4. Adjust heights (if heightmap provided)
5. Generate `.tscn` file at `GodotProject/levels/Kursk.tscn`

### With Heightmap (Recommended)

```bash
python3 tools/portal_convert.py \
    --map Kursk \
    --base-terrain MP_Tungsten \
    --heightmap GodotProject/terrain/Kursk_heightmap.png \
    --terrain-size 2048 \
    --min-height 73 \
    --max-height 217
```

### Custom Output Location

```bash
python3 tools/portal_convert.py \
    --map Kursk \
    --base-terrain MP_Tungsten \
    --output GodotProject/levels/Kursk_v2.tscn
```

---

## Prerequisites

### 1. Extracted BF1942 Maps

Extract RFA archives first using BGA or WinRFA:

```
bf1942_source/
└── extracted/
    └── Bf1942/
        └── Archives/
            └── bf1942/
                └── Levels/
                    ├── Kursk/
                    ├── Wake_Island/
                    └── ...
```

**See:** [BF1942 Data Structures](./BF1942_Data_Structures.md#rfa-refractor-archive) for extraction details.

### 2. Asset Mappings

Ensure mappings exist:

```bash
ls tools/asset_audit/bf1942_to_portal_mappings.json
# Should show 733 mapped assets
```

If missing, run:
```bash
python3 tools/create_asset_mappings.py --auto-suggest
```

### 3. Portal SDK

Ensure Portal SDK is set up in `GodotProject/`:

```bash
ls FbExportData/asset_types.json
# Should show 6,292 Portal assets
```

---

## Available Tools

### `portal_convert.py` - Master CLI

Full conversion pipeline from BF1942 to Portal format.

**Usage:**
```bash
python3 tools/portal_convert.py --map <name> --base-terrain <terrain> [options]
```

**Required Arguments:**
- `--map <name>` - Map name (e.g., `Kursk`, `Wake_Island`)
- `--base-terrain <terrain>` - Portal base terrain (e.g., `MP_Tungsten`, `MP_Outskirts`)

**Optional Arguments:**
- `--bf1942-root <path>` - Custom BF1942 maps directory (default: `bf1942_source/extracted/Bf1942/Archives/bf1942/Levels`)
- `--output <path>` - Custom output .tscn path (default: `GodotProject/levels/<MapName>.tscn`)
- `--heightmap <path>` - Path to heightmap PNG for terrain height sampling
- `--terrain-size <meters>` - Terrain size in meters (default: 2048)
- `--min-height <meters>` - Minimum terrain height (default: 0)
- `--max-height <meters>` - Maximum terrain height (default: 200)

**Examples:**

Basic conversion:
```bash
python3 tools/portal_convert.py --map Kursk --base-terrain MP_Tungsten
```

With heightmap (recommended):
```bash
python3 tools/portal_convert.py \
    --map Kursk \
    --base-terrain MP_Tungsten \
    --heightmap GodotProject/terrain/Kursk_heightmap.png \
    --min-height 73 \
    --max-height 217
```

Custom paths:
```bash
python3 tools/portal_convert.py \
    --map Wake_Island \
    --base-terrain MP_Outskirts \
    --bf1942-root /custom/path/to/bf1942/maps \
    --output GodotProject/levels/Wake.tscn
```

**Output:**
- `.tscn` file at specified output location
- Console log showing conversion progress
- Asset mapping statistics

---

### `portal_parse.py` - Parser Only

Extract data from BF1942 maps without converting to Portal format.

**Usage:**
```bash
python3 tools/portal_parse.py --map <name> [--output <json_path>]
```

**Purpose:** Debug parsing, inspect map data, validate extraction before full conversion.

**Example:**
```bash
python3 tools/portal_parse.py --map Kursk --output debug/kursk_data.json
```

---

### `portal_map_assets.py` - Asset Mapper

Map BF1942 assets to Portal equivalents using mapping database.

**Usage:**
```bash
python3 tools/portal_map_assets.py --input <parsed_data.json> --output <mapped_data.json>
```

**Purpose:** Test asset mappings, debug mapping issues, customize mappings.

**Example:**
```bash
python3 tools/portal_map_assets.py \
    --input debug/kursk_data.json \
    --output debug/kursk_mapped.json
```

---

### `portal_adjust_heights.py` - Height Adjuster

Adjust object heights to match Portal terrain (re-runnable).

**Usage:**
```bash
python3 tools/portal_adjust_heights.py \
    --input <tscn_file> \
    --output <adjusted_tscn> \
    --heightmap <png_path> \
    --terrain-size <meters>
```

**Purpose:** Re-adjust heights when switching base terrains, fix floating/underground objects.

**Example:**
```bash
python3 tools/portal_adjust_heights.py \
    --input GodotProject/levels/Kursk.tscn \
    --output GodotProject/levels/Kursk_fixed.tscn \
    --heightmap GodotProject/terrain/Tungsten_heightmap.png \
    --terrain-size 2048
```

> 💡 **Tip:** This tool is re-runnable. If heights look wrong, run it again with adjusted parameters.

---

### `portal_rebase.py` - Terrain Switcher

Switch Portal base terrain without re-converting from BF1942.

**Usage:**
```bash
python3 tools/portal_rebase.py \
    --input <tscn_file> \
    --output <new_tscn> \
    --new-base-terrain <terrain>
```

**Purpose:** Try different Portal base terrains quickly without full re-conversion.

**Example:**
```bash
python3 tools/portal_rebase.py \
    --input GodotProject/levels/Kursk.tscn \
    --output GodotProject/levels/Kursk_outskirts.tscn \
    --new-base-terrain MP_Outskirts
```

**What it does:**
1. Parses existing `.tscn` (no BF1942 re-parsing)
2. Re-centers objects for new terrain
3. Re-adjusts heights for new terrain mesh
4. Generates new `.tscn` with new base terrain reference

> 📝 **Note:** Much faster than full re-conversion. Use this to experiment with different Portal base maps.

---

### `portal_generate.py` - Scene Generator

Generate `.tscn` file from processed data.

**Usage:**
```bash
python3 tools/portal_generate.py \
    --input <mapped_data.json> \
    --output <tscn_file> \
    --base-terrain <terrain>
```

**Purpose:** Final step in modular pipeline, custom .tscn generation.

---

### `portal_validate.py` - Validator

Validate `.tscn` files for Portal compatibility.

**Usage:**
```bash
python3 tools/portal_validate.py <tscn_file>
```

**Purpose:** Check for errors, missing required nodes, invalid asset references.

**Example:**
```bash
python3 tools/portal_validate.py GodotProject/levels/Kursk.tscn
```

**Checks:**
- Required nodes present (TEAM_1_HQ, TEAM_2_HQ, CombatArea, Static)
- Minimum spawn points per team (4+)
- Valid asset references
- Transform matrices valid
- No floating/underground objects (if heightmap provided)

---

## Configuration Files

### Game Configs

**Location:** `tools/configs/games/`

**Example:** `bf1942.json`
```json
{
  "name": "BF1942",
  "engine": "Refractor 1.0",
  "era": "WW2",
  "expansions": ["base", "xpack1_rtr", "xpack2_sw"]
}
```

**Purpose:** Define game metadata, engine version, available expansions.

### Map Configs

**Location:** `tools/configs/maps/bf1942/`

**Example:** `kursk.json`
```json
{
  "name": "Kursk",
  "game": "BF1942",
  "theme": "open_terrain",
  "recommended_base_terrain": "MP_Tungsten",
  "dimensions": {
    "width": 2048,
    "height": 2048
  },
  "height_range": {
    "min": 73,
    "max": 217
  }
}
```

**Purpose:** Store map-specific metadata, recommended Portal base terrain, dimensions.

---

## Workflows

### Workflow A: BF1942 → Portal (Initial Conversion)

Full conversion from source game to Portal format.

**Steps:**
1. **Extract RFA archives** (if needed)
   ```bash
   # Use BGA or WinRFA on Windows
   # Or use Wine on macOS/Linux
   ```

2. **Run conversion**
   ```bash
   python3 tools/portal_convert.py --map Kursk --base-terrain MP_Tungsten
   ```

3. **Open in Godot**
   - Open `GodotProject/` in Godot 4
   - Open `levels/Kursk.tscn`

4. **Review and adjust**
   - Check spawn points
   - Verify asset placements
   - Adjust positions if needed

5. **Export**
   - Click BFPortal panel → "Export Current Level"
   - Upload `.spatial.json` to Portal web builder

### Workflow B: Portal → Portal (Base Terrain Switch)

Switch Portal base terrain without re-parsing BF1942 data.

**Steps:**
1. **Start with existing `.tscn`**
   ```bash
   ls GodotProject/levels/Kursk.tscn
   ```

2. **Run rebase tool**
   ```bash
   python3 tools/portal_rebase.py \
       --input GodotProject/levels/Kursk.tscn \
       --output GodotProject/levels/Kursk_limestone.tscn \
       --new-base-terrain MP_Limestone
   ```

3. **Review in Godot**
   - Open new `.tscn` file
   - Verify re-centering and heights

4. **Export and test**

> ⚡ **Advantage:** 10x faster than full re-conversion. No BF1942 re-parsing or re-mapping needed.

---

## Troubleshooting

### "Map directory not found"

**Cause:** BF1942 map not extracted or wrong path.

**Solution:**
```bash
# Verify extraction
ls bf1942_source/extracted/Bf1942/Archives/bf1942/Levels/Kursk

# Or specify custom path
python3 tools/portal_convert.py \
    --map Kursk \
    --base-terrain MP_Tungsten \
    --bf1942-root /custom/path/to/levels
```

### "Mappings file not found"

**Cause:** Asset mapping database missing.

**Solution:**
```bash
# Create mappings
python3 tools/create_asset_mappings.py --auto-suggest

# Verify
ls tools/asset_audit/bf1942_to_portal_mappings.json
```

### "Asset mapping failed"

**Cause:** Portal asset has `levelRestrictions` and isn't available on target map.

**Solution:** The mapper automatically tries fallbacks. Check console output for:
```
Warning: Asset 'PineTree' not available on MP_Tungsten, using fallback 'BirchTree'
```

If many failures, consider different base terrain.

### "Heights are incorrect" / "Objects floating/underground"

**Cause:** No heightmap provided, or heightmap doesn't match Portal terrain.

**Solution:**
```bash
# Provide heightmap
python3 tools/portal_convert.py \
    --map Kursk \
    --base-terrain MP_Tungsten \
    --heightmap GodotProject/terrain/Kursk_heightmap.png \
    --min-height 73 \
    --max-height 217
```

Or re-run height adjustment:
```bash
python3 tools/portal_adjust_heights.py \
    --input GodotProject/levels/Kursk.tscn \
    --output GodotProject/levels/Kursk_fixed.tscn \
    --heightmap GodotProject/terrain/Tungsten_heightmap.png
```

### "Coordinate offset looks wrong" / "Objects outside CombatArea"

**Cause:** Map center calculation issue or scale mismatch.

**Solution:** Open in Godot and check:
1. Are most objects centered in CombatArea?
2. Select a few objects and verify positions are reasonable
3. If completely wrong, may need to debug coordinate transform

See: [Troubleshooting Guide](../guides/Troubleshooting.md) for comprehensive solutions.

---

## Architecture

```
portal_convert.py (CLI)
    ↓ orchestrates
bfportal/ (Core Library)
    ├── engines/refractor/
    │   └── games/bf1942.py          # Parse BF1942 .con files
    ├── mappers/asset_mapper.py       # Map assets using database
    ├── transforms/coordinate_offset.py # Calculate offsets
    ├── terrain/terrain_provider.py    # Sample terrain heights
    └── generators/tscn_generator.py   # Generate .tscn files
```

**Design:** Modular pipeline with SOLID principles. Each tool uses core library components.

**See Also:**
- [Architecture Plan](../architecture/BF_TO_PORTAL_TOOLSET_PLAN.md) - Complete system design
- [Multi-Game Support](../architecture/Multi_Era_Support.md) - Extensibility for other Battlefield games

---

**Last Updated:** October 2025
**Status:** Production Ready
**Tools Version:** 1.0

**See Also:**
- [Converting Your First Map](../tutorials/Converting_Your_First_Map.md) - Step-by-step tutorial
- [BF1942 Data Structures](./BF1942_Data_Structures.md) - Source game format reference
- [Troubleshooting Guide](../guides/Troubleshooting.md) - Common issues and solutions
- [Main README](../../README.md) - Project overview
