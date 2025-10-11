# BF1942 to Portal Conversion Project

Automated conversion pipeline for bringing classic Battlefield 1942 maps into Battlefield 2042 Portal.

## Overview

This project converts Battlefield 1942 maps to BF2042 Portal format, preserving gameplay layout, spawn points, and asset placement while mapping classic assets to modern Portal equivalents.

**Status**: ✅ Production-ready with 95.3% conversion accuracy

## Features

- **Automated Conversion Pipeline**: Single command converts any BF1942 map
- **Intelligent Asset Mapping**: 3-tier fallback system with 733 BF1942 → Portal mappings
- **Terrain-Aware Placement**: Mesh-based height sampling with bilinear interpolation
- **Type-Smart Fallbacks**: Trees map to trees, buildings to buildings (not generic props)
- **Multi-Terrain Support**: Convert to any Portal base terrain (MP_Tungsten, MP_Battery, etc.)
- **Orientation Detection**: Automatic map rotation calculation
- **SOLID Architecture**: Modular, extensible, DRY codebase

## Quick Start

### Prerequisites

- Python 3.8+
- Godot 4.5 (Standard, not .NET)
- Portal SDK installed
- Extracted BF1942 map files

### Installation

```bash
git clone https://github.com/zachatkinson/bf1942-portal-conversion.git
cd PortalSDK

# Install Portal SDK .glb files to GodotProject/raw/models/
# (Portal SDK files not included in git due to size)
```

### Convert a Map

```bash
python3 tools/portal_convert.py --map Kursk --base-terrain MP_Tungsten
```

Output: `GodotProject/levels/Kursk.tscn`

### Test in Godot

1. Open `GodotProject/` in Godot 4.5
2. Open `levels/Kursk.tscn`
3. Use BFPortal panel → "Export Current Level"
4. Upload `.spatial.json` to Portal web builder

## Conversion Results (Kursk Example)

| Metric | Value |
|--------|-------|
| **Assets Mapped** | 1439/1510 (95.3%) |
| **Terrain** | MP_Tungsten (flat, 35.7m elevation range) |
| **Trees** | Pine/Spruce → Birch |
| **Buildings** | Barns/Mills → Portal equivalents |
| **Combat Area** | 1122m × 1222m (matches BF1942) |

## Architecture

```
tools/bfportal/
├── core/           # Interfaces, exceptions, data models
├── engines/        # Game engine parsers (BF1942 Refractor)
├── mappers/        # Asset mapping with intelligent fallbacks
├── terrain/        # Mesh-based terrain provider
├── transforms/     # Coordinate systems and offsetting
├── generators/     # .tscn file generation
├── orientation/    # Map orientation detection
└── validation/     # Map validation tools
```

### Key Components

**Intelligent Fallback System:**
1. Map-specific fallbacks (e.g., fences → Hesco barriers on MP_Tungsten)
2. Category-based alternatives with type matching (tree→tree, not rock)
3. Full Portal catalog search for type keyword matches
4. Best-guess fallback using name heuristics
5. Terrain element detection (water bodies skipped with notes)

**Terrain Alignment:**
- Detects non-centered Portal terrain meshes
- Centers assets at actual mesh center (not assumed origin)
- 256×256 height grid with bilinear interpolation
- All spatial queries use real mesh bounds

## Supported Maps

- ✅ **Kursk** (completed, tested)
- 🔜 Wake Island
- 🔜 El Alamein
- 🔜 Stalingrad
- 🔜 Guadalcanal
- 🔜 All other BF1942 maps

## Advanced Usage

### Custom Terrain

```bash
python3 tools/portal_convert.py \
  --map Wake_Island \
  --base-terrain MP_Limestone \
  --output GodotProject/levels/Wake_Island_v2.tscn
```

### Custom BF1942 Path

```bash
python3 tools/portal_convert.py \
  --map Berlin \
  --base-terrain MP_Outskirts \
  --bf1942-root /path/to/bf1942/maps
```

## Project Structure

```
PortalSDK/
├── bf1942_source/          # BF1942 extracted maps (gitignored)
├── GodotProject/           # Portal Godot project
│   ├── levels/            # Converted maps (.tscn)
│   ├── raw/models/        # Portal SDK .glb files (gitignored)
│   └── static/            # Portal terrain meshes
├── FbExportData/          # Portal asset catalog & exports
├── tools/
│   ├── bfportal/         # Conversion pipeline modules
│   ├── asset_audit/      # Asset mapping database
│   └── portal_convert.py # Main CLI tool
└── README.html            # Portal SDK documentation
```

## Known Limitations

- **Water Bodies**: Portal SDK has limited water support. Lakes/rivers are skipped with notes.
- **Asset Restrictions**: Some Portal assets only work on specific maps (handled via fallbacks).
- **Manual Terrain**: Portal doesn't support custom terrain import. Must use existing base maps.

## Development

Built with:
- **SOLID Principles**: Single Responsibility, Dependency Inversion
- **Clean Interfaces**: `IGameEngine`, `IAssetMapper`, `ITerrainProvider`
- **Type Safety**: Full Python type hints throughout
- **Extensibility**: Easy to add support for BF:Vietnam, BF2, etc.

### Run Conversion with Debug Output

```bash
python3 tools/portal_convert.py --map Kursk --base-terrain MP_Tungsten 2>&1 | tee conversion.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow existing code style (SOLID, DRY, type hints)
4. Test with at least one map conversion
5. Submit pull request

## Resources

- [Portal SDK Documentation](./README.html) (original EA/DICE docs)
- [Unofficial Portal Docs](https://github.com/NodotProject/Unofficial-BF6-Portal-SDK-Docs)
- [BF1942 Modding Community](https://bfmods.com)

## License

This conversion toolset is provided as-is for educational and modding purposes.

Battlefield 1942 and Battlefield 2042 are trademarks of Electronic Arts Inc.

## Credits

**Author**: Zach Atkinson
**AI Assistant**: Claude (Anthropic)
**Date**: October 2025

Built with the Portal SDK provided by EA/DICE.
