# Documentation

> Comprehensive guides, references, and architecture docs for the Battlefield to Portal conversion project

[![Docs](https://img.shields.io/badge/docs-comprehensive-blue.svg)](./README.md)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](./README.md)

**Last Updated:** October 2025
**Status:** Production Ready

---

## Table of Contents

- [Getting Started](#getting-started)
- [Documentation Structure](#documentation-structure)
  - [Tutorials](#tutorials)
  - [Guides](#guides)
  - [Reference](#reference)
  - [Examples](#examples)
  - [Architecture](#architecture)
  - [Setup](#setup)
- [Learning Path](#learning-path)
- [Contributing](#contributing)
- [Additional Resources](#additional-resources)

---

## Getting Started

New to the project? Start here:

1. 📖 **[Project README](../README.md)** - Project overview, features, and quick start
2. ⚙️ **[Godot Setup Guide](./setup/Godot_Setup_Guide.md)** - Install and configure Godot 4 for Portal development
3. 🎓 **[Converting Your First Map](./tutorials/Converting_Your_First_Map.md)** - Step-by-step tutorial for first conversion
4. 🧪 **[Testing Guide](../TESTING.md)** - Validate your converted maps
5. 🍎 **[macOS Users](./setup/macOS_Compatibility_Patch.md)** - macOS-specific setup instructions

---

## Documentation Structure

### Tutorials

Step-by-step guides for learning the conversion process:

| Document | Description | Difficulty | Time |
|----------|-------------|------------|------|
| [**Converting Your First Map**](./tutorials/Converting_Your_First_Map.md) | Complete walkthrough from extraction to in-game testing (uses Kursk as example) | Beginner | ~45 min |

**Topics Covered:**
- RFA extraction (Windows/macOS/Linux)
- Portal base terrain selection
- Running the conversion pipeline
- Godot verification steps
- Export to Portal format
- In-game testing

### Guides

Focused how-to guides for specific tasks:

| Document | Description |
|----------|-------------|
| [**Troubleshooting Guide**](./guides/Troubleshooting.md) | Comprehensive solutions for 40+ common issues across extraction, conversion, Godot, export, and in-game problems |

**Topics Covered:**
- Extraction issues (RFA failures, missing files)
- Conversion failures (path errors, mapping issues)
- Coordinate problems (floating/underground objects)
- Asset mapping issues (level restrictions, fallbacks)
- Godot editor problems (import failures, missing plugins)
- Export troubleshooting (JSON validation, manual export)

### Reference

Technical specifications and command documentation:

| Document | Description |
|----------|-------------|
| [**CLI Tools Reference**](./reference/CLI_Tools.md) | Complete command-line tool documentation for all conversion tools with examples and troubleshooting |
| [**BF1942 Data Structures**](./reference/BF1942_Data_Structures.md) | Complete reference for BF1942 file formats (.con, .rfa, heightmaps) and coordinate systems |

**CLI Tools Topics:**
- portal_convert.py (master CLI)
- Modular tools (parse, map, adjust, rebase, generate, validate)
- Configuration files (game configs, map configs)
- Workflow types (BF1942→Portal, Portal→Portal)

**Data Structures Topics:**
- .CON file syntax and structure
- .RFA archive format
- Map directory layouts
- Object spawn formats
- Heightmap specifications

### Examples

Real-world conversion case studies and results:

| Document | Description | Result |
|----------|-------------|--------|
| [**Kursk Conversion**](./examples/Kursk_Conversion.md) | Detailed analysis of Kursk map conversion showing challenges, solutions, and 100% authenticity achievement | 95.3% asset accuracy, 100% gameplay authentic |

**Topics Covered:**
- 7 technical challenges encountered
- Solutions implemented for each issue
- Before/after comparisons
- Performance metrics (time, file sizes)
- Asset breakdown and mapping success rate
- Lessons learned and best practices
- Verification checklist

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

---

## Learning Path

### For New Users

1. **Understand the Goal** - Read [Project README](../README.md)
2. **Set Up Your Environment** - Follow [Godot Setup Guide](./setup/Godot_Setup_Guide.md)
3. **Convert Your First Map** - Complete [Converting Your First Map](./tutorials/Converting_Your_First_Map.md) tutorial
4. **Learn from Examples** - Study [Kursk Conversion](./examples/Kursk_Conversion.md) case study
5. **Get Help When Stuck** - Use [Troubleshooting Guide](./guides/Troubleshooting.md)

### For Developers

1. **Architecture Overview** - Read [Toolset Plan](./architecture/BF_TO_PORTAL_TOOLSET_PLAN.md)
2. **Multi-Game Design** - Study [Multi-Game Support](./architecture/Multi_Era_Support.md)
3. **Source Formats** - Reference [BF1942 Data Structures](./reference/BF1942_Data_Structures.md)
4. **CLI Tools** - Master [CLI Tools Reference](./reference/CLI_Tools.md) for command usage
5. **Code Standards** - Review [CLAUDE.md](../.claude/CLAUDE.md) for coding conventions

### For Contributors

1. **Read Contributing Guide** - Start with [CONTRIBUTING.md](../CONTRIBUTING.md) for complete guidelines
2. **Architecture Principles** - Understand SOLID/DRY patterns in [Toolset Plan](./architecture/BF_TO_PORTAL_TOOLSET_PLAN.md)
3. **Adding New Games** - Follow the guide in [Multi-Game Support](./architecture/Multi_Era_Support.md#adding-a-new-game)
4. **Code Quality** - Ensure compliance with project standards in [CONTRIBUTING.md](../CONTRIBUTING.md#code-standards)
5. **Submit Changes** - Follow the [PR process](../CONTRIBUTING.md#submitting-changes)

---

## Contributing

We welcome contributions! Please read our [**Contributing Guide**](../CONTRIBUTING.md) for complete details.

**Quick Ways to Help:**

- 🐛 **Report Issues** - Found a bug or documentation error? [Open an issue](https://github.com/yourusername/PortalSDK/issues)
- 📝 **Improve Docs** - Submit fixes or enhancements to documentation
- 🎮 **Add Game Support** - Implement new game engines following [Multi-Game Support](./architecture/Multi_Era_Support.md)
- 🗺️ **Convert Maps** - Test the pipeline with new maps and report results
- 🔧 **Fix Bugs** - Check open issues and submit PRs
- ✨ **Add Features** - Propose and implement new capabilities

**See:** [CONTRIBUTING.md](../CONTRIBUTING.md) for code standards, testing requirements, and PR process.

---

## Additional Resources

### Project Documentation

- [Main README](../README.md) - Project overview and quick start
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines and code standards
- [TESTING.md](../TESTING.md) - Testing procedures and validation
- [Portal SDK Docs](../README.html) - Official EA/DICE Portal SDK documentation

### External Resources

- [Godot 4 Documentation](https://docs.godotengine.org/en/stable/)
- [BF1942 Modding Community](https://bfmods.com)
- [Unofficial Portal SDK Docs](https://github.com/NodotProject/Unofficial-BF6-Portal-SDK-Docs)

### Internal Documentation

Some documentation remains in `.claude/` for AI assistant context:
- `.claude/CLAUDE.md` - Comprehensive project instructions
- `.claude/Kursk_Authenticity_Report.md` - Detailed conversion quality analysis

---

**Last Updated:** October 2025
**Documentation Version:** 1.0
**Project Status:** Production Ready

**Questions or Feedback?**
- 💬 Discussions - [GitHub Discussions](https://github.com/yourusername/PortalSDK/discussions)
- 🐛 Bug Reports - [GitHub Issues](https://github.com/yourusername/PortalSDK/issues)

**See Also:**
- [Project README](../README.md) - Main project overview
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [Style Guide](./STYLE_GUIDE.md) - Documentation standards
- [TESTING.md](../TESTING.md) - Testing procedures
