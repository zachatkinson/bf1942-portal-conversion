# Portal Conversion CLI Tools

## Quick Start

### 1. Convert a BF1942 Map

```bash
python3 tools/portal_convert.py --map Kursk --base-terrain MP_Tungsten
```

This will:
1. Parse BF1942 Kursk map files
2. Map 733 assets to Portal equivalents
3. Calculate coordinate offsets
4. Adjust heights to terrain mesh
5. Generate `.tscn` file

### 2. Custom Output Location

```bash
python3 tools/portal_convert.py \
    --map Kursk \
    --base-terrain MP_Tungsten \
    --output GodotProject/levels/Kursk_v2.tscn
```

### 3. Different Terrain Size

```bash
python3 tools/portal_convert.py \
    --map Kursk \
    --base-terrain MP_Tungsten \
    --terrain-size 1536
```

## Prerequisites

### 1. Extracted BF1942 Maps

Extract RFA archives first:
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

### 2. Asset Mappings

Ensure mappings exist:
```bash
ls tools/asset_audit/bf1942_to_portal_mappings.json
# Should show 733 mapped assets
```

### 3. Portal SDK

Ensure Portal SDK is set up:
```bash
ls FbExportData/asset_types.json
# Should show 6,292 Portal assets
```

## Available Tools

### `portal_convert.py` - Master CLI

Full conversion pipeline from BF1942 to Portal.

**Usage:**
```bash
python3 tools/portal_convert.py --map <name> --base-terrain <terrain>
```

**Options:**
- `--map` - Map name (required)
- `--base-terrain` - Portal base terrain (required)
- `--bf1942-root` - Custom BF1942 maps directory
- `--output` - Custom output .tscn path
- `--terrain-size` - Terrain size in meters (default: 2048)

**Examples:**

Basic:
```bash
python3 tools/portal_convert.py --map Kursk --base-terrain MP_Tungsten
```

Custom terrain size:
```bash
python3 tools/portal_convert.py \
    --map Kursk \
    --base-terrain MP_Tungsten \
    --terrain-size 1536
```

Custom paths:
```bash
python3 tools/portal_convert.py \
    --map Wake_Island \
    --base-terrain MP_Outskirts \
    --bf1942-root /path/to/bf1942/maps \
    --output GodotProject/levels/Wake.tscn
```

### `portal_rebase.py` - Switch Base Terrains

Switch Portal base terrain without re-converting from BF1942.

**Usage:**
```bash
python3 tools/portal_rebase.py \
    --input GodotProject/levels/Kursk.tscn \
    --output GodotProject/levels/Kursk_outskirts.tscn \
    --new-base MP_Outskirts
```

**Options:**
- `--input` - Input .tscn file (required)
- `--output` - Output .tscn file (required)
- `--new-base` - Target Portal base terrain (required)
- `--heightmap` - Custom heightmap PNG file
- `--terrain-size` - Terrain size in meters (default: 2048)
- `--min-height` - Minimum terrain height (default: 0)
- `--max-height` - Maximum terrain height (default: 200)
- `--map-center-x` - Override map center X coordinate
- `--map-center-z` - Override map center Z coordinate

**Status**: ✅ Implemented with 97% test coverage

### `portal_validate.py` - Validate Maps

Validate .tscn files for Portal compatibility.

**Usage:**
```bash
python3 tools/portal_validate.py GodotProject/levels/Kursk.tscn
```

**Options:**
- `maps` - .tscn files to validate (positional, one or more)
- `--sdk-root` - Portal SDK root directory (default: current directory)
- `--strict` - Treat warnings as errors

**Status**: ✅ Implemented with 97% test coverage

### `portal_parse.py` - Parse BF1942 Maps

Parse BF1942/Vietnam/BF2/2142 maps to extract gameplay data without conversion.

**Usage:**
```bash
python3 tools/portal_parse.py --game bf1942 --map-path bf1942_source/extracted/.../Kursk
```

**Options:**
- `--game` - Source game engine: bf1942, bfvietnam, bf2, bf2142 (required)
- `--map-path` - Path to extracted map directory (required)
- `--output` - Output file (optional, prints to stdout if not specified)
- `--format` - Output format: json or summary (default: summary)
- `--verbose` - Verbose output with debug information

### `portal_map_assets.py` - Map Assets to Portal

Map source game assets to Portal equivalents independently from parsing or generation.

**Usage:**
```bash
python3 tools/portal_map_assets.py --game bf1942 --input kursk_parsed.json
```

**Options:**
- `--game` - Source game engine: bf1942, bfvietnam, bf2, bf2142 (required)
- `--input` - Input JSON file from portal_parse.py
- `--output` - Output JSON file with mappings
- `--assets` - Comma-separated list of asset names to map
- `--mappings-file` - Custom asset mappings JSON file
- `--map-theme` - Map theme: desert, urban, forest, snow, tropical, open_terrain (default: open_terrain)
- `--stats-only` - Only show mapping statistics, do not write output
- `--verbose` - Verbose output with mapping details

### `portal_adjust_heights.py` - Adjust Object Heights

Adjust object heights in a .tscn file to match terrain. Can be run multiple times (idempotent).

**Usage:**
```bash
python3 tools/portal_adjust_heights.py --input Kursk.tscn --heightmap Kursk.png --in-place
```

**Options:**
- `--input` - Input .tscn file (required)
- `--output` - Output .tscn file (required unless --in-place)
- `--in-place` - Modify input file directly (overwrites input)
- `--heightmap` - Custom heightmap PNG file
- `--base-terrain` - Use Portal base terrain provider: MP_Tungsten or MP_Outskirts
- `--terrain-size` - Terrain size in meters (default: 2048)
- `--min-height` - Minimum terrain height (default: 0)
- `--max-height` - Maximum terrain height (default: 200)
- `--ground-offset` - Additional offset above ground in meters (default: 0)
- `--tolerance` - Height difference tolerance (default: 2.0m)
- `--dry-run` - Show what would be adjusted without modifying files

### `validate_tscn.py` - Validate TSCN Files

Validates generated .tscn files against BF6 Portal requirements.

**Usage:**
```bash
python3 tools/validate_tscn.py GodotProject/levels/Kursk.tscn
```

**Options:**
- Positional argument: path to .tscn file

### `validate_conversion.py` - Validate Conversions

Validates BF1942 to Portal conversion accuracy with mathematical verification.

**Usage:**
```bash
python3 tools/validate_conversion.py --source bf1942_source/.../Kursk --output GodotProject/levels/Kursk.tscn
```

**Options:**
- `--source` - Path to source BF1942 map directory (required)
- `--output` - Path to generated .tscn file (required)
- `--heightmap` - Path to heightmap PNG (optional)
- `--terrain-size` - Terrain size in meters (default: 2048)
- `--min-height` - Minimum terrain height (default: 70)
- `--max-height` - Maximum terrain height (default: 220)

### `export_to_portal.py` - Export to Portal

Export a Godot .tscn map to complete Battlefield 6 Portal experience format.

**Usage:**
```bash
python3 tools/export_to_portal.py Kursk
```

**Options:**
- `map_name` - Name of the map to export (positional, required)
- `--base-map` - Base map to use for terrain (default: MP_Tungsten)
- `--max-players` - Maximum players per team: 16, 32, or 64 (default: 32)
- `--game-mode` - Game mode: Conquest, Rush, TeamDeathmatch, Breakthrough (default: Conquest)
- `--description` - Custom description for the experience
- `--tscn-path` - Custom path to .tscn file

### `create_experience.py` - Create Experience File

Create a complete Portal experience file from an existing .spatial.json file.

**Usage:**
```bash
python3 tools/create_experience.py Kursk
```

**Options:**
- `map_name` - Name of the map (positional, required)
- `--spatial-path` - Path to .spatial.json file
- `--base-map` - Base map for terrain (default: MP_Tungsten)
- `--max-players` - Maximum players per team: 16, 32, or 64 (default: 32)
- `--game-mode` - Game mode: Conquest, Rush, TeamDeathmatch, Breakthrough (default: Conquest)
- `--description` - Custom description for the experience

### `create_multi_map_experience.py` - Multi-Map Experiences

Create multi-map Portal experiences from the maps registry.

**Usage:**
```bash
python3 tools/create_multi_map_experience.py
```

**Options:**
- `--template` - Experience template from registry (default: all_maps_conquest)
- `--maps` - Specific map IDs to include (overrides template filter)
- `--name` - Override experience name from template
- `--description` - Override experience description from template
- `--game-mode` - Override game mode: Conquest, Rush, TeamDeathmatch, Breakthrough
- `--max-players` - Override max players per team: 16, 32, or 64
- `--registry` - Path to maps registry (default: maps_registry.json)
- `--output` - Output path for experience file

### `rfa_extractor.py` - RFA Extraction Tool

Extract files from Battlefield 1942 RFA archives (guidance tool, recommends external tools).

**Usage:**
```bash
python3 tools/rfa_extractor.py <input.rfa> <output_dir>
```

**Options:**
- Positional: input RFA file path
- Positional: output directory path

### `scan_all_maps.py` - Scan All Maps

Comprehensive asset scanner for ALL extracted BF1942 maps. Discovers unique asset types across base game + expansions.

**Usage:**
```bash
python3 tools/scan_all_maps.py
```

**Options:**
- No command-line arguments

### `complete_asset_analysis.py` - Asset Coverage Analysis

Analyzes all asset sources and identifies gaps in mapping coverage.

**Usage:**
```bash
python3 tools/complete_asset_analysis.py
```

**Options:**
- No command-line arguments

### `filter_real_assets.py` - Filter Real Assets

Filter real assets from map scan results using intelligent classification.

**Usage:**
```bash
python3 tools/filter_real_assets.py
```

**Options:**
- No command-line arguments

### `generate_portal_index.py` - Generate Portal Asset Index

Generate Portal asset indexes from Portal SDK asset_types.json.

**Usage:**
```bash
python3 tools/generate_portal_index.py
```

**Options:**
- No command-line arguments

### `compare_terrains.py` - Compare Terrains

Compare available BF6 Portal terrains for map conversion (informational script).

**Usage:**
```bash
python3 tools/compare_terrains.py
```

**Options:**
- No command-line arguments

## Configuration Files

### Game Configs

Location: `tools/configs/games/`

Example: `bf1942.json`
```json
{
  "name": "BF1942",
  "engine": "Refractor 1.0",
  "era": "WW2",
  "expansions": ["base", "xpack1_rtr", "xpack2_sw"]
}
```

### Map Configs

Location: `tools/configs/maps/bf1942/`

Example: `kursk.json`
```json
{
  "name": "Kursk",
  "game": "BF1942",
  "theme": "open_terrain",
  "recommended_base_terrain": "MP_Tungsten",
  "dimensions": {
    "width": 2048,
    "height": 2048
  }
}
```

## Workflow

### Workflow A: BF1942 → Portal (Initial Conversion)

1. Extract RFA archives (if needed)
2. Run `portal_convert.py`
3. Open `.tscn` in Godot
4. Review and adjust
5. Export via BFPortal panel

### Workflow B: Portal → Portal (Base Terrain Switch)

1. Start with existing `.tscn`
2. Run `portal_rebase.py`
3. Re-centers and re-adjusts heights
4. No re-parsing or re-mapping needed

## Troubleshooting

### "Map directory not found"

Ensure BF1942 maps are extracted:
```bash
ls bf1942_source/extracted/Bf1942/Archives/bf1942/Levels/Kursk
```

### "Mappings file not found"

Run asset mapper first:
```bash
python3 tools/create_asset_mappings.py --auto-suggest
```

### "Asset mapping failed"

Check level restrictions - some Portal assets are map-specific.
The mapper will try to find unrestricted alternatives.

### "Heights are incorrect"

Use the portal_adjust_heights.py tool to adjust heights after conversion:
```bash
python3 tools/portal_adjust_heights.py \
    --input GodotProject/levels/Kursk.tscn \
    --heightmap GodotProject/terrain/Kursk_heightmap.png \
    --in-place
```

## Architecture

```
portal_convert.py (CLI)
    ↓ uses
bfportal/ (Core Library)
    ├── engines/refractor/
    │   └── games/bf1942.py
    ├── mappers/asset_mapper.py
    ├── transforms/coordinate_offset.py
    └── terrain/terrain_provider.py
```

See `.claude/BF_To_Portal_Toolset_Plan.md` for complete architecture.

## Development

### Add a New Map Config

1. Create `tools/configs/maps/bf1942/<map_name>.json`
2. Follow `kursk.json` template
3. Specify recommended base terrain

### Add a New Game

1. Create game config: `tools/configs/games/<game>.json`
2. Create engine: `bfportal/engines/refractor/games/<game>.py`
3. Extend `RefractorEngine` base class

## Test Suite

Comprehensive testing with 787 tests:

```bash
# Run all tests
python3 -m pytest tools/tests/ -v

# Run with coverage
python3 -m pytest tools/tests/ --cov=tools/bfportal --cov-report=html

# View HTML report
open tools/tests/htmlcov/index.html
```

See:
- `tools/tests/README.md` - Test documentation
- `tools/tests/Coverage_Report.md` - Coverage report

## Support

- **Master Plan**: `docs/architecture/BF_To_Portal_Toolset_Plan.md`
- **Project Docs**: `.claude/CLAUDE.md`
- **Test Suite**: `tools/tests/README.md`

---

**Status**: ✅ Production-ready (Sprint 3 complete)
**Last Updated**: 2025-10-12
