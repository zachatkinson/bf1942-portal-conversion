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
4. Adjust heights (if heightmap provided)
5. Generate `.tscn` file

### 2. With Heightmap (Recommended)

```bash
python3 tools/portal_convert.py \
    --map Kursk \
    --base-terrain MP_Tungsten \
    --heightmap GodotProject/terrain/Kursk_heightmap.png \
    --terrain-size 2048 \
    --min-height 73 \
    --max-height 217
```

### 3. Custom Output Location

```bash
python3 tools/portal_convert.py \
    --map Kursk \
    --base-terrain MP_Tungsten \
    --output GodotProject/levels/Kursk_v2.tscn
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
- `--heightmap` - Path to heightmap PNG
- `--terrain-size` - Terrain size in meters (default: 2048)
- `--min-height` - Minimum terrain height (default: 0)
- `--max-height` - Maximum terrain height (default: 200)

**Examples:**

Basic:
```bash
python3 tools/portal_convert.py --map Kursk --base-terrain MP_Tungsten
```

With heightmap:
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
    --new-base-terrain MP_Outskirts
```

**Status**: ✅ Implemented with 97% test coverage

### `portal_validate.py` - Validate Maps

Validate .tscn files for Portal compatibility.

**Usage:**
```bash
python3 tools/portal_validate.py GodotProject/levels/Kursk.tscn
```

**Status**: ✅ Implemented with 97% test coverage

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

Provide a heightmap:
```bash
python3 tools/portal_convert.py \
    --map Kursk \
    --base-terrain MP_Tungsten \
    --heightmap GodotProject/terrain/Kursk_heightmap.png
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

See `.claude/BF_TO_PORTAL_TOOLSET_PLAN.md` for complete architecture.

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

Comprehensive testing with 241 tests:

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
- `tools/tests/COVERAGE_REPORT.md` - Coverage report

## Support

- **Master Plan**: `docs/architecture/BF_TO_PORTAL_TOOLSET_PLAN.md`
- **Project Docs**: `.claude/CLAUDE.md`
- **Test Suite**: `tools/tests/README.md`

---

**Status**: ✅ Production-ready (Sprint 3 complete)
**Last Updated**: 2025-10-12
