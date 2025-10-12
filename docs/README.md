# Documentation

> Comprehensive guides, references, and architecture docs for the Battlefield to Portal conversion project

[![Docs](https://img.shields.io/badge/docs-comprehensive-blue.svg)](./README.md)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](./README.md)

**Last Updated:** October 2025
**Status:** Production Ready

## Table of Contents

- [Getting Started](#getting-started)
- [Documentation Structure](#documentation-structure)
  - [Architecture](#architecture)
  - [Reference](#reference)
  - [Setup](#setup)
  - [Examples](#examples)
- [Learning Path](#learning-path)
- [Contributing](#contributing)
- [Additional Resources](#additional-resources)

---

## Getting Started

New to the project? Start here:

1. 📖 **[Project README](../README.md)** - Project overview, features, and quick start
2. ⚙️ **[Godot Setup Guide](./setup/Godot_Setup_Guide.md)** - Install and configure Godot 4 for Portal development
3. 🧪 **[Testing Guide](../TESTING.md)** - Validate your converted maps
4. 🍎 **[macOS Users](./setup/macOS_Compatibility_Patch.md)** - macOS-specific setup instructions

---

## Documentation Structure

### Architecture

System design and technical architecture:

| Document | Description |
|----------|-------------|
| [**BF_TO_PORTAL_TOOLSET_PLAN**](./architecture/BF_TO_PORTAL_TOOLSET_PLAN.md) | Master architecture plan, SOLID design principles, modular CLI structure |
| [**Multi-Game Support Architecture**](./architecture/Multi_Era_Support.md) | Extensible design for supporting all Battlefield games (BF1942, Vietnam, BF2, 2142, Frostbite) |

**Key Topics:**
- SOLID/DRY principles
- Interface-based design (IGameEngine, IAssetMapper, ITerrainProvider)
- Modular CLI architecture
- Multi-game conversion pipeline

### Reference

Technical specifications and data format documentation:

| Document | Description |
|----------|-------------|
| [**BF1942 Data Structures**](./reference/BF1942_Data_Structures.md) | Complete reference for BF1942 file formats (.con, .rfa, heightmaps) and coordinate systems |

**Key Topics:**
- .CON file syntax and structure
- .RFA archive format
- Map directory layouts
- Object spawn formats
- Heightmap specifications

### Setup

Installation and environment configuration:

| Document | Description |
|----------|-------------|
| [**Godot Setup Guide**](./setup/Godot_Setup_Guide.md) | Complete guide for installing Godot 4 and opening Portal SDK projects |
| [**macOS Compatibility**](./setup/macOS_Compatibility_Patch.md) | macOS-specific workarounds and manual export procedures |

**Platforms Covered:**
- ✅ Windows (full support)
- ✅ macOS (with workarounds)
- ✅ Linux (full support)

### Examples

> 🚧 **Coming Soon:** Conversion examples, case studies, and best practices

---

## Learning Path

### For New Users

1. **Understand the Goal** - Read [Project README](../README.md)
2. **Set Up Your Environment** - Follow [Godot Setup Guide](./setup/Godot_Setup_Guide.md)
3. **Test the Pipeline** - Run the [Testing Guide](../TESTING.md) procedures
4. **Convert Your First Map** - See [Tools CLI Documentation](../tools/README_CLI.md)

### For Developers

1. **Architecture Overview** - Read [Toolset Plan](./architecture/BF_TO_PORTAL_TOOLSET_PLAN.md)
2. **Multi-Game Design** - Study [Multi-Game Support](./architecture/Multi_Era_Support.md)
3. **Source Formats** - Reference [BF1942 Data Structures](./reference/BF1942_Data_Structures.md)
4. **Code Standards** - Review [CLAUDE.md](../.claude/CLAUDE.md) for coding conventions

### For Contributors

1. **Architecture Principles** - Understand SOLID/DRY patterns in [Toolset Plan](./architecture/BF_TO_PORTAL_TOOLSET_PLAN.md)
2. **Adding New Games** - Follow the guide in [Multi-Game Support](./architecture/Multi_Era_Support.md#adding-a-new-game)
3. **Code Quality** - Ensure compliance with project standards
4. **Submit Changes** - (See CONTRIBUTING.md when available)

---

## Contributing

We welcome contributions! While our formal contribution guide is in progress, here's how you can help:

- 🐛 **Report Issues** - Found a bug or documentation error? [Open an issue](https://github.com/yourusername/PortalSDK/issues)
- 📝 **Improve Docs** - Submit fixes or enhancements to documentation
- 🎮 **Add Game Support** - Implement new game engines following [Multi-Game Support](./architecture/Multi_Era_Support.md)
- 🗺️ **Convert Maps** - Test the pipeline with new maps and report results

---

## Additional Resources

### Project Documentation

- [Main README](../README.md) - Project overview and quick start
- [TESTING.md](../TESTING.md) - Testing procedures and validation
- [Portal SDK Docs](../README.html) - Official EA/DICE Portal SDK documentation
- [Tools CLI Guide](../tools/README_CLI.md) - Command-line tool usage (local)

### External Resources

- [Godot 4 Documentation](https://docs.godotengine.org/en/stable/)
- [BF1942 Modding Community](https://bfmods.com)
- [Unofficial Portal SDK Docs](https://github.com/NodotProject/Unofficial-BF6-Portal-SDK-Docs)

### Internal Documentation

Some documentation remains in `.claude/` for AI assistant context:
- `.claude/CLAUDE.md` - Comprehensive project instructions
- `.claude/Kursk_Authenticity_Report.md` - Detailed conversion quality analysis

---

## Questions or Feedback?

- 💬 **Discussions** - [GitHub Discussions](https://github.com/yourusername/PortalSDK/discussions)
- 🐛 **Bug Reports** - [GitHub Issues](https://github.com/yourusername/PortalSDK/issues)
- 📧 **Contact** - (Your contact method)

---

**Last Updated:** October 2025
**Documentation Version:** 1.0
**Project Status:** Production Ready
