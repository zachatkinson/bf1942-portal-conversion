# BF1942 to BF6 Portal Conversion Tools

This directory contains tools for converting Battlefield 1942 maps to Battlefield 6 Portal format.

**Status**: ✅ Production-ready with 787-test suite (Sprint 3 complete)

**Requirements**: Python 3.13+ (uses modern type hints and syntax)

## Quick Start

```bash
# Convert a BF1942 map
python3 tools/portal_convert.py --map Kursk --base-terrain MP_Tungsten

# Output: GodotProject/levels/Kursk.tscn
```

## Architecture

This toolset uses a modular SOLID architecture:

```
tools/
├── portal_convert.py          # Master CLI (orchestrator)
├── portal_parse.py            # Parse BF1942 data
├── portal_map_assets.py       # Map assets
├── portal_adjust_heights.py   # Adjust heights
├── portal_rebase.py           # Switch base terrains
├── portal_validate.py         # Validate maps
└── bfportal/                  # Core library
    ├── core/                  # Interfaces, data models
    ├── engines/refractor/     # BF1942/BFV parsing
    ├── mappers/               # Asset mapping
    ├── terrain/               # Height sampling
    ├── transforms/            # Coordinate transforms
    ├── generators/            # .tscn generation
    └── validation/            # Map validation
```

See `README_CLI.md` for detailed command documentation.

## Available Tools

### Core Conversion Pipeline

**`portal_convert.py`** - Master orchestrator for end-to-end conversion
```bash
python3 tools/portal_convert.py --map Kursk --base-terrain MP_Tungsten
```
Coordinates the entire BF1942→Portal conversion pipeline: parse → map → transform → generate.

**`portal_parse.py`** - Parse BF1942 map data from extracted files
```bash
python3 tools/portal_parse.py --source bf1942_source/extracted/.../Kursk
```
Extracts gameplay objects, spawn points, and metadata from BF1942 .con files.

**`portal_map_assets.py`** - Map BF1942 assets to Portal equivalents
```bash
python3 tools/portal_map_assets.py --input parsed_data.json --output mapped_data.json
```
Translates BF1942 asset types to corresponding BF6 Portal assets using mapping database.

**`portal_adjust_heights.py`** - Adjust object heights to match Portal terrain
```bash
python3 tools/portal_adjust_heights.py --map Kursk --heightmap terrain.png
```
Samples Portal terrain heightmap and adjusts object Y-coordinates for proper placement.

**`portal_rebase.py`** - Switch base terrain for existing maps
```bash
python3 tools/portal_rebase.py --map Kursk --new-terrain MP_Capstone
```
Changes the underlying Portal terrain while preserving object placements.

### Validation & Quality Assurance

**`portal_validate.py`** - Comprehensive map validation
```bash
python3 tools/portal_validate.py --map Kursk
```
Validates Portal map requirements: HQs, spawns, combat area, asset placement.

**`validate_tscn.py`** - TSCN file structure validation
```bash
python3 tools/validate_tscn.py GodotProject/levels/Kursk.tscn
```
Validates .tscn syntax: required nodes, spawn counts, ObjIds, transforms, node paths.

**`validate_conversion.py`** - Mathematical conversion accuracy validation
```bash
python3 tools/validate_conversion.py --source bf1942_source/.../Kursk \
                                     --output GodotProject/levels/Kursk.tscn
```
Verifies coordinate transformations, height adjustments, rotation accuracy, bounds checking.

### Portal Export & Experience Creation

**`export_to_portal.py`** - Complete Portal experience export
```bash
python3 tools/export_to_portal.py Kursk --base-map MP_Tungsten --max-players 32
```
Exports .tscn → .spatial.json → complete experience.json ready for Portal import.

**`create_experience.py`** - Create experience from existing .spatial.json
```bash
python3 tools/create_experience.py Kursk --base-map MP_Tungsten --max-players 64
```
Wraps existing .spatial.json in Portal experience format with metadata and settings.

**`create_multi_map_experience.py`** - Multi-map rotation experiences
```bash
python3 tools/create_multi_map_experience.py --maps kursk el_alamein wake_island
```
Creates Portal experiences with multiple BF1942 maps in rotation from registry.

### Asset Management & Analysis

**`scan_all_maps.py`** - Comprehensive BF1942 asset discovery
```bash
python3 tools/scan_all_maps.py
```
Scans all 36 extracted BF1942 maps (base + expansions) and catalogs every unique asset type.

**`complete_asset_analysis.py`** - Asset coverage gap analysis
```bash
python3 tools/complete_asset_analysis.py
```
Analyzes Portal assets, BF1942 catalog, mapping table, and identifies missing mappings.

**`filter_real_assets.py`** - Intelligent asset classification
```bash
python3 tools/filter_real_assets.py
```
Uses classification system to distinguish real assets (vehicles, buildings) from metadata (spawn points).

**`generate_portal_index.py`** - Portal asset catalog generation
```bash
python3 tools/generate_portal_index.py
```
Creates searchable indexes and browsable catalogs from Portal SDK asset_types.json.

### Terrain & Comparison Tools

**`compare_terrains.py`** - Portal terrain comparison for map matching
```bash
python3 tools/compare_terrains.py
```
Compares available BF6 Portal terrains and scores them for suitability to BF1942 maps.

## Test Suite

The conversion tools have comprehensive test coverage:

- **Total Tests**: 787 (all passing)
- **Coverage**: 98% overall
- **Test Files**: 9 test modules + integration tests

See:
- `tools/tests/README.md` - Test documentation
- `tools/tests/Coverage_Report.md` - Coverage analysis

Run tests:
```bash
python3 -m pytest tools/tests/ -v
```

## References

- **Documentation**: `README_CLI.md` - Detailed CLI reference
- **Architecture**: `.claude/BF_To_Portal_Toolset_Plan.md` - SOLID design
- **BGA GitHub**: https://github.com/yann-papouin/bga
- **BF1942 Modding**: https://bfmods.com/mdt/
- **RFA Format**: https://www.realtimerendering.com/erich/bf1942/mdt/tutorials/Overview/Overview.html

---

**Status**: Production-ready (Sprint 3 complete)
**Last Updated**: 2025-10-12

## Historical Context: Phase 1 RFA Extraction

This section documents the initial research phase for extracting BF1942 map data. The conversion pipeline now assumes maps are already extracted.

### RFA Format Background

BF1942 map data is stored in .rfa (Refractor Archive) files using LZO compression. The toolset includes `rfa_extractor.py` which provides guidance but requires external tools for actual extraction.

### Extraction Tools Available

1. **BGA (Battlefield Game Archive)** - https://github.com/yann-papouin/bga
   - Most comprehensive Windows tool
   - GUI with preview, extract, and repack capabilities

2. **WinRFA** - Classic BF1942 modding tool with simple GUI

3. **rfaUnpack.exe** - Command-line extractor from BF1942 modding toolkit

### Current Status

- ✅ Research complete - RFA format documented
- ✅ Extraction approach: Use BGA tool on Windows
- ✅ All conversion tools work with pre-extracted data
- ✅ Kursk and other maps successfully extracted and converted

### Expected Directory Structure After Extraction

```
bf1942_source/
└── extracted/
    └── Bf1942/
        └── Archives/
            └── bf1942/
                └── Levels/
                    └── Kursk/
                        ├── Info/               # Map metadata
                        │   └── Kursk.desc
                        ├── Gameplay/           # Gameplay objects
                        │   ├── Objects.con
                        │   ├── Spawns.con
                        │   └── ...
                        ├── Heightmap/          # Terrain data
                        │   └── HeightMap.raw
                        └── Textures/           # Terrain textures
```

### Future Automation (Phase 3)

For fully automated extraction, a Python RFA parser would need:
1. Reverse engineered RFA binary format implementation
2. Header/file table parsing
3. LZO decompression integration (`python-lzo`)
4. Command-line interface

This remains a future enhancement opportunity but is not required for the current conversion pipeline.