# Battlefield to Portal Conversion Project

> Automated conversion pipeline for bringing classic Battlefield maps into Battlefield 6 Portal

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey.svg)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)
![Conversion Accuracy](https://img.shields.io/badge/conversion%20accuracy-95.3%25-success.svg)

---

Currently supports Battlefield 1942 with extensible architecture for all Battlefield games.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Conversion Results](#conversion-results-kursk-example)
- [Architecture](#architecture)
- [Supported Maps](#supported-maps)
- [Advanced Usage](#advanced-usage)
- [Project Structure](#project-structure)
- [Known Limitations](#known-limitations)
- [Development](#development)
- [Contributing](#contributing)
- [Additional Resources](#additional-resources)
- [License](#license)

## Overview

This project converts classic Battlefield game maps to BF6 Portal format, preserving gameplay layout, spawn points, and asset placement while mapping classic assets to modern Portal equivalents.

**Current Status**: ✅ Battlefield 1942 production-ready with 95.3% conversion accuracy

**Roadmap**: Support for all Battlefield games:
- ✅ **Battlefield 1942** (Base + Road to Rome + Secret Weapons)
- 🔜 **Battlefield Vietnam**
- 🔜 **Battlefield 2** (Base + Special Forces + Armored Fury + Euro Force)
- 🔜 **Battlefield 2142**
- 🔜 **Bad Company 1 & 2**
- 🔜 **Battlefield 3**
- 🔜 **Battlefield 4**
- 🔜 **Battlefield Hardline**
- 🔜 **Battlefield 1**
- 🔜 **Battlefield V**
- 🔜 **Battlefield 2042**

## Features

- **Automated Conversion Pipeline**: Single command converts any supported Battlefield map
- **Intelligent Asset Mapping**: Multi-tier fallback system with 733+ asset mappings
- **Terrain-Aware Placement**: Mesh-based height sampling with bilinear interpolation
- **Type-Smart Fallbacks**: Trees map to trees, buildings to buildings (not generic props)
- **Multi-Terrain Support**: Convert to any Portal base terrain (MP_Tungsten, MP_Battery, etc.)
- **Orientation Detection**: Automatic map rotation calculation
- **Multi-Game Engine Support**: Extensible architecture for all Battlefield engines
- **SOLID Architecture**: Modular, clean interfaces make adding new games straightforward

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
├── engines/        # Game engine parsers (Refractor, Frostbite, etc.)
│   └── refractor/  # BF1942 + BFV implementation
├── mappers/        # Asset mapping with intelligent fallbacks
├── terrain/        # Mesh-based terrain provider
├── transforms/     # Coordinate systems and offsetting
├── generators/     # .tscn file generation
├── orientation/    # Map orientation detection
└── validation/     # Map validation tools
```

**Multi-Game Architecture**: The `IGameEngine` interface allows easy addition of new Battlefield games. Each game engine implements:
- Map file parsing (RFA, LVL, etc.)
- Coordinate system handling
- Asset extraction
- Game-specific logic (conquest points, spawns, etc.)

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

### Battlefield 1942

- ✅ **Kursk** (completed, tested in Portal)
- 🔜 Wake Island
- 🔜 El Alamein
- 🔜 Stalingrad
- 🔜 Guadalcanal
- 🔜 All other BF1942 base maps + expansions

### Other Battlefield Games

Coming soon - the architecture is designed to easily add parsers for other Battlefield engines.

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
- **Extensibility**: Easy to add support for all Battlefield games via engine abstraction

### Development Tools

This project uses modern Python tooling for code quality:

**Ruff** - Fast Python linter and formatter (10-100x faster than Black/flake8):
```bash
# Install ruff
pip install ruff

# Format code
ruff format tools/

# Lint code
ruff check tools/

# Auto-fix issues
ruff check --fix tools/
```

**mypy** - Static type checker:
```bash
# Install mypy
pip install mypy

# Type check codebase
mypy tools/
```

All configuration is in `pyproject.toml`.

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

## Additional Resources

### Project Documentation

- [Documentation Hub](./docs/README.md) - Complete documentation index
- [Architecture Guide](./docs/architecture/Multi_Era_Support.md) - Multi-game architecture
- [BF1942 Reference](./docs/reference/BF1942_Data_Structures.md) - File format reference
- [Setup Guide](./docs/setup/Godot_Setup_Guide.md) - Godot installation

### External Resources

- [Portal SDK Documentation](./README.html) - Original EA/DICE Portal SDK docs
- [Unofficial Portal Docs](https://github.com/NodotProject/Unofficial-BF6-Portal-SDK-Docs) - Community documentation
- [BF1942 Modding Community](https://bfmods.com) - Classic BF modding resources
- [Godot 4 Documentation](https://docs.godotengine.org/en/stable/) - Godot engine docs

## License

This conversion toolset is provided as-is for educational and modding purposes.

Battlefield 1942 and Battlefield 6 are trademarks of Electronic Arts Inc.

---

**Last Updated:** October 2025
**Project Status:** Production Ready
**Author:** Zach Atkinson
**AI Assistant:** Claude (Anthropic)

Built with the Portal SDK provided by EA/DICE.

**See Also:**
- [Documentation](./docs/README.md) - Full documentation
- [Testing Guide](./TESTING.md) - Validation procedures
- [Style Guide](./docs/STYLE_GUIDE.md) - Documentation standards
