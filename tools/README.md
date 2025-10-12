# BF1942 to BF6 Portal Conversion Tools

This directory contains tools for converting Battlefield 1942 maps to Battlefield 6 Portal format.

**Status**: ✅ Production-ready with 241-test suite (Sprint 3 complete)

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

## Phase 1: RFA Extraction

### Current Situation

BF1942 map data is stored in .rfa (Refractor Archive) files using LZO compression.

### RFA Extraction Approaches

#### Option 1: Use Existing Windows Tools (RECOMMENDED)

**Tools Available:**
1. **BGA (Battlefield Game Archive)** - https://github.com/yann-papouin/bga
   - Most comprehensive tool
   - Written in Pascal/Delphi
   - GUI + potential command-line support
   - Can preview files, extract, and repack

2. **WinRFA** - Classic BF1942 modding tool
   - Simple Windows GUI
   - Extract and pack RFA files

3. **rfaUnpack.exe** - Command-line extractor
   - Part of BF1942 modding toolkit

**How to Use on Mac:**
Since we're on macOS and Wine isn't installed:

1. **Option A**: Ask user to extract RFAs on Windows gaming PC
   - Run BGA or WinRFA on gaming PC
   - Extract all Kursk files
   - Copy extracted folder to Mac: `bf1942_source/extracted/Kursk/`

2. **Option B**: Install Wine/CrossOver and run BGA
   - Install Wine: `brew install --cask wine-stable`
   - Run BGA.exe via Wine
   - Extract directly on Mac

3. **Option C**: Find/create Python RFA parser (Phase 3 task)
   - Implement full RFA format parser
   - Requires reverse engineering RFA binary format
   - Time-intensive but provides automation

#### Option 2: Python Implementation (FUTURE - Phase 3)

For full automation, we'll need to:
1. Reverse engineer RFA binary format
2. Implement header/file table parsing
3. Add LZO decompression support (via `python-lzo`)
4. Create command-line extraction tool

**Dependencies needed:**
```bash
pip3 install python-lzo
# Or with uv (recommended):
uv pip install python-lzo

# On Linux: sudo apt-get install liblzo2-dev
```

### Current Tool: `rfa_extractor.py`

Located: `/tools/rfa_extractor.py`

**Status**: Skeleton implementation, provides guidance
**Usage**:
```bash
python3 tools/rfa_extractor.py <input.rfa> <output_dir>
# Or with uv (recommended):
uv run tools/rfa_extractor.py <input.rfa> <output_dir>
```

Currently displays instructions for using external tools.

### Phase 1 Status

- ✅ Research RFA format and available tools
- ✅ RFA extraction approach: Use BGA tool on Windows
- ✅ Kursk map extracted and converted
- ✅ BF1942 data structures documented
- ✅ Conversion pipeline implemented

**Note**: `rfa_extractor.py` provides guidance for extraction but requires external tools (BGA, WinRFA) for actual extraction.

## File Structure After Extraction

Expected structure after RFA extraction:

```
bf1942_source/
└── extracted/
    └── Kursk/
        ├── Info/               # Map metadata
        │   └── Kursk.desc      # Map description
        ├── Gameplay/           # Gameplay objects
        │   ├── Objects.con     # Object placements
        │   ├── Spawns.con      # Spawn points
        │   └── ...
        ├── Heightmap/          # Terrain data
        │   └── HeightMap.raw
        ├── Textures/           # Terrain textures
        └── ...
```

## Test Suite

The conversion tools have comprehensive test coverage:

- **Total Tests**: 241 (237 passing, 1 skipped)
- **Coverage**: 64% overall
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

