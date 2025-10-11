# BF1942 to BF6 Portal Conversion Tools

This directory contains tools for converting Battlefield 1942 maps to Battlefield 6 Portal format.

## Phase 1: RFA Extraction Status

### Current Situation

BF1942 map data is stored in .rfa (Refractor Archive) files using LZO compression. We have three Kursk files:
- `Kursk.rfa` - Main map archive (10.4 MB)
- `Kursk_000.rfa` - Patch file  (68 KB)
- `Kursk_003.rfa` - Patch file (14 KB)

### RFA Extraction Approaches

After researching available options, here are the recommended approaches:

#### Option 1: Use Existing Windows Tools (RECOMMENDED FOR NOW)

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

### Next Steps for Phase 1

1. ✅ Research RFA format and available tools
2. ⏳ **DECISION NEEDED**: Choose extraction approach
   - Ask user to extract on Windows PC?
   - Install Wine and use BGA?
   - Defer to Phase 3 for Python implementation?
3. Extract Kursk map files
4. Analyze extracted .con files for object data
5. Document BF1942 data structures

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

## References

- BGA GitHub: https://github.com/yann-papouin/bga
- BF1942 Modding Tutorials: https://bfmods.com/mdt/
- RFA Format Info: https://www.realtimerendering.com/erich/bf1942/mdt/tutorials/Overview/Overview.html

