# Contributing to BF1942 Portal Conversion

> Guidelines for contributing to the Battlefield to Portal conversion project

**Last Updated:** October 2025

---

## Table of Contents

- [Welcome](#welcome)
- [Ways to Contribute](#ways-to-contribute)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Documentation Standards](#documentation-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Community Guidelines](#community-guidelines)

---

## Welcome

Thank you for your interest in contributing to the BF1942 Portal Conversion project! This project aims to bring classic Battlefield maps to modern Battlefield 6 Portal, and we welcome contributions of all types.

### What We're Building

A comprehensive, maintainable toolset for converting classic Battlefield maps (1942, Vietnam, BF2, 2142, and beyond) to Battlefield 6 Portal format, with proper SOLID/DRY compliance and extensibility.

### Current Status

- ✅ **BF1942 Support:** Production-ready (95.3% conversion accuracy)
- 🔜 **BF Vietnam:** Planned (shares Refractor 1.0 engine)
- 📅 **BF2/2142:** Future (Refractor 2.0 engine)
- 📅 **Frostbite Games:** Long-term (BF3, BF4, BF1, BFV, 2042)

---

## Ways to Contribute

### 1. Report Issues

Found a bug or documentation error?

- 🐛 [Open an issue](https://github.com/yourusername/PortalSDK/issues)
- Provide: OS, Python version, exact command used, error message
- Include: Debug output (see [Troubleshooting Guide](docs/guides/Troubleshooting.md))

### 2. Improve Asset Mappings

Help map BF1942 assets to better Portal equivalents.

**File:** `tools/asset_audit/bf1942_to_portal_mappings.json`

**How to help:**
```json
{
  "vehicles": {
    "lighttankspawner": {
      "portal_equivalent": "VEH_Leopard",  // Update with better match
      "category": "vehicle",
      "confidence_score": 0.8,  // Your confidence (0.0-1.0)
      "notes": "Why this mapping is appropriate"
    }
  }
}
```

**Testing your changes:**
```bash
python3 tools/portal_convert.py --map Kursk --base-terrain MP_Tungsten
# Verify in Godot that your mapping looks correct
```

### 3. Convert and Document New Maps

Convert additional BF1942 maps and document results.

**Process:**
1. Convert map following [Tutorial](docs/tutorials/Converting_Your_First_Map.md)
2. Document issues encountered
3. Share results and screenshots
4. Update map compatibility list

**Maps we'd love to see:**
- Wake Island
- El Alamein
- Stalingrad
- Omaha Beach
- Battle of Britain

### 4. Add New Game Support

Implement support for other Battlefield games.

**See:** [Multi-Game Support Architecture](docs/architecture/Multi_Era_Support.md#adding-a-new-game)

**Steps:**
1. Create game engine (e.g., `bfportal/engines/refractor/games/bfvietnam.py`)
2. Create asset mapping file (`tools/asset_audit/bfvietnam_to_portal_mappings.json`)
3. Register engine in `engines/__init__.py`
4. Test with 2-3 maps
5. Document in README

### 5. Improve Documentation

- Fix typos or unclear instructions
- Add screenshots or diagrams
- Write additional tutorials
- Translate documentation

**See:** [Documentation Style Guide](docs/STYLE_GUIDE.md)

### 6. Code Contributions

- Fix bugs
- Add features
- Optimize performance
- Improve error handling

---

## Getting Started

### Prerequisites

- Python 3.8+
- Godot 4.3+
- Git
- BF1942 game files (for testing)

### Fork and Clone

```bash
# Fork repository on GitHub
# Then clone your fork:
git clone https://github.com/yourusername/PortalSDK.git
cd PortalSDK

# Add upstream remote:
git remote add upstream https://github.com/zachatkinson/PortalSDK.git
```

### Set Up Development Environment

```bash
# Install Python dependencies (if adding new features)
pip install -r requirements.txt  # When available

# Install development tools
pip install ruff mypy  # Linting and type checking

# Verify setup
python3 tools/portal_convert.py --help
```

### Run Tests

```bash
# Validate existing conversions
python3 tools/portal_validate.py GodotProject/levels/Kursk.tscn

# Test conversion pipeline
python3 tools/portal_convert.py --map Kursk --base-terrain MP_Tungsten

# Verify in Godot
godot GodotProject/project.godot
```

---

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

**Branch naming:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions

### 2. Make Changes

- Follow [Code Standards](#code-standards)
- Follow [Documentation Standards](#documentation-standards)
- Test your changes thoroughly

### 3. Commit Changes

**Format:** `<type>: <description>`

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `refactor` - Code refactoring
- `test` - Test additions
- `chore` - Build/tooling changes

**Example:**
```bash
git add .
git commit -m "feat: add BF Vietnam engine support"
```

**Good commit messages:**
```
feat: add heightmap support to portal_convert.py
fix: correct coordinate offset calculation for large maps
docs: add troubleshooting section for asset mapping errors
refactor: extract coordinate transform logic to separate module
```

### 4. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create PR on GitHub
# Provide clear description of changes
# Reference related issues (#123)
```

---

## Code Standards

### Python Code Style

**Follow PEP 8:**
```bash
# Format code with Ruff
ruff format tools/

# Lint code
ruff check tools/

# Fix auto-fixable issues
ruff check --fix tools/
```

**Type hints required:**
```python
def parse_map(map_path: Path, context: MapContext) -> MapData:
    """Parse a BF1942 map from extracted files.

    Args:
        map_path: Path to extracted map directory
        context: Conversion context (game, base terrain, etc.)

    Returns:
        MapData with objects, spawns, control points

    Raises:
        FileNotFoundError: If map directory doesn't exist
        ParseError: If .con files are malformed
    """
    pass
```

**Naming conventions:**
- `snake_case` for functions and variables
- `PascalCase` for classes
- `UPPER_CASE` for constants
- Descriptive names (no `x`, `tmp`, `data`)

### Architecture Principles

**SOLID Design:**
- **S**ingle Responsibility - Each class/function does one thing
- **O**pen/Closed - Open for extension, closed for modification
- **L**iskov Substitution - Subclasses can replace base classes
- **I**nterface Segregation - Many specific interfaces, not one general
- **D**ependency Inversion - Depend on abstractions, not concretions

**DRY (Don't Repeat Yourself):**
- Extract common logic to functions/classes
- Use inheritance for shared behavior
- Configuration over duplication

**Example:**
```python
# Good: Interface-based design
class IGameEngine(ABC):
    @abstractmethod
    def parse_map(self, map_path: Path) -> MapData:
        pass

class BF1942Engine(RefractorEngine):
    def parse_map(self, map_path: Path) -> MapData:
        # BF1942-specific implementation
        pass

# Bad: Hardcoded game logic
def parse_map(map_path: Path, game: str) -> MapData:
    if game == "BF1942":
        # BF1942 logic
    elif game == "BFVietnam":
        # Duplicate logic
    # ... more if/else
```

### Code Quality

**Type checking:**
```bash
mypy tools/
```

**Expected:** No errors (100% type coverage goal)

---

## Documentation Standards

### Follow the Style Guide

All documentation must follow [Documentation Style Guide](docs/STYLE_GUIDE.md).

**Key requirements:**
- Headers: tagline, Purpose, Last Updated, Status
- Table of contents (if >150 lines)
- Code blocks with language specification
- Cross-references with context
- Professional footer

### Documentation Types

**Tutorials:**
- Step-by-step instructions
- Target audience: Beginner
- Include time estimates
- Provide verification steps

**Reference:**
- Complete technical specifications
- Target audience: All levels
- Include examples
- Cross-reference related concepts

**Guides:**
- How-to accomplish specific tasks
- Target audience: Intermediate
- Focus on solutions, not theory

### Updating Documentation

When adding features:
1. Update relevant reference docs
2. Add tutorial if needed
3. Update troubleshooting if applicable
4. Cross-reference from related docs

---

## Testing

### Manual Testing Checklist

Before submitting PR, verify:

**For conversion changes:**
- [ ] Convert Kursk successfully
- [ ] Open in Godot without errors
- [ ] Spawn points present (5 Axis, 4 Allies for Kursk)
- [ ] Export to .spatial.json succeeds
- [ ] JSON validates

**For new game support:**
- [ ] Convert 2-3 maps from new game
- [ ] Document conversion accuracy (% assets mapped)
- [ ] Test in Godot
- [ ] Update README with supported maps

**For asset mapping changes:**
- [ ] Test with affected map
- [ ] Verify visual correctness in Godot
- [ ] Check no regressions (other maps still work)

### Automated Tests (Future)

We plan to add:
- Unit tests for parsers
- Integration tests for full pipeline
- Regression tests for known maps

---

## Submitting Changes

### Pull Request Checklist

- [ ] Branch follows naming convention
- [ ] Code follows style guide (run `ruff format` and `ruff check`)
- [ ] Type hints added (run `mypy`)
- [ ] Documentation updated
- [ ] Changes tested manually
- [ ] Commit messages descriptive
- [ ] PR description explains changes

### PR Description Template

```markdown
## What does this PR do?

Brief description of changes.

## Why?

Explain motivation and context.

## How was this tested?

- [ ] Converted Kursk successfully
- [ ] Verified in Godot
- [ ] (Other specific tests)

## Related Issues

Fixes #123
Related to #456

## Screenshots (if applicable)

(Add screenshots showing before/after)
```

### Review Process

1. **Automated checks** - Code style, type checking
2. **Maintainer review** - Code quality, architecture fit
3. **Testing** - Manual verification of changes
4. **Merge** - Squash and merge to main branch

**Feedback:** Be responsive to review comments. We're here to help!

---

## Community Guidelines

### Code of Conduct

- **Be respectful** - Treat everyone with respect
- **Be constructive** - Provide helpful feedback
- **Be patient** - Contributors have varying experience levels
- **Be inclusive** - Welcome diverse perspectives

### Communication

**Preferred channels:**
- 💬 GitHub Discussions - General questions, ideas
- 🐛 GitHub Issues - Bug reports, feature requests
- 📧 Direct contact - Security issues only

**Response times:**
- Issues: 1-3 days
- PRs: 3-7 days
- Discussions: Best effort (community-driven)

### Recognition

Contributors will be:
- Listed in [README.md](README.md) credits
- Mentioned in commit messages (Co-Authored-By)
- Credited in documentation they create

---

## Questions?

**Not sure where to start?**
- Check [Good First Issues](https://github.com/yourusername/PortalSDK/labels/good%20first%20issue)
- Read [Converting Your First Map](docs/tutorials/Converting_Your_First_Map.md) tutorial
- Ask in [GitHub Discussions](https://github.com/yourusername/PortalSDK/discussions)

**Found this guide unclear?**
- Open an issue to improve it!
- Documentation contributions are highly valued

---

**Last Updated:** October 2025
**Status:** Active - Contributions Welcome

**See Also:**
- [Documentation Style Guide](docs/STYLE_GUIDE.md) - Writing standards
- [Multi-Game Support](docs/architecture/Multi_Era_Support.md) - Adding new games
- [CLI Tools Reference](docs/reference/CLI_Tools.md) - Command documentation
- [Main README](README.md) - Project overview
