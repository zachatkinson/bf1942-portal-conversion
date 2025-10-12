# Documentation Style Guide

> Comprehensive standards and best practices based on industry-leading open source projects

**Purpose:** Standards and best practices for all PortalSDK documentation
**Last Updated:** October 2025
**Status:** Official Standard

---

## Table of Contents

- [Document Types](#document-types)
- [Header Structure](#header-structure)
- [Badges](#badges)
- [Table of Contents](#table-of-contents-1)
- [Content Formatting](#content-formatting)
- [Code Blocks](#code-blocks)
- [Cross-References](#cross-references)
- [Admonitions](#admonitions)
- [Footer Pattern](#footer-pattern)
- [File Naming](#file-naming)
- [Document Templates](#document-templates)
- [Checklist for New Documents](#checklist-for-new-documents)
- [Examples from This Project](#examples-from-this-project)

---

## Document Types

### Root README.md
**Purpose:** Project overview, quick start, features
**Required Elements:**
- Project title and tagline
- Badges (build, version, license, language, platforms)
- Quick start guide
- Feature highlights
- Links to detailed docs
- Contributing section
- License

### docs/README.md
**Purpose:** Documentation navigation hub
**Required Elements:**
- Documentation overview
- Directory structure with descriptions
- Learning paths (new users, developers, contributors)
- Quick links to key documents
- External resources

### Architecture Docs
**Purpose:** System design, technical decisions
**Required Elements:**
- Clear diagrams (ASCII or linked images)
- Interface definitions
- Design patterns used
- Examples of usage

### Reference Docs
**Purpose:** Technical specifications, API reference
**Required Elements:**
- Complete data structure definitions
- Code examples
- Cross-references to related concepts

### Setup Guides
**Purpose:** Installation and configuration
**Required Elements:**
- Prerequisites
- Step-by-step instructions
- Platform-specific sections
- Troubleshooting
- Verification steps

---

## Header Structure

### Standard Header (All Documents)

```markdown
# Document Title

**Purpose:** One-line description of what this document covers
**Last Updated:** October 2025
**Status:** Production Ready | Beta | Alpha | Deprecated | Reference Only

[Optional badges here - see Badges section]

---
```

### Specialized Headers

**For Architecture Docs:**
```markdown
# Architecture: Component Name

**Purpose:** What this architecture document explains
**Last Updated:** October 2025
**Status:** ✅ Implemented | 🚧 In Progress | 📅 Planned
**Complexity:** Low | Medium | High
```

**For Guides:**
```markdown
# Guide: Task Name

**Purpose:** What you'll learn
**Last Updated:** October 2025
**Difficulty:** Beginner | Intermediate | Advanced
**Time Required:** ~X minutes
```

---

## Badges

### When to Use Badges

**Root README.md - Always Include:**
```markdown
![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey.svg)
```

**docs/README.md - Documentation Hub:**
```markdown
[![Docs](https://img.shields.io/badge/docs-latest-blue.svg)](./README.md)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](./README.md)
```

**Individual Docs - Rarely:**
- Only use status badges for deprecated/beta features
- Most individual docs don't need badges

### Badge Colors (shields.io)
- `brightgreen` - Success, production, passing
- `green` - Stable, approved
- `blue` - Information, documentation
- `orange` - Warning, beta
- `red` - Error, deprecated, failing
- `lightgrey` - Neutral information

---

## Table of Contents

### When Required
- Documents **>150 lines** must have TOC
- Documents **>50 lines** should have TOC
- Short docs (<50 lines) don't need TOC

### Format
```markdown
## Table of Contents

- [Section 1](#section-1)
  - [Subsection 1.1](#subsection-11)
  - [Subsection 1.2](#subsection-12)
- [Section 2](#section-2)
- [Section 3](#section-3)

---
```

**Rules:**
- Place immediately after header
- Use h2 (`##`) for "Table of Contents" heading
- Include separator (`---`) after TOC
- Keep TOC updated when adding/removing sections
- Use kebab-case for anchor links

---

## Content Formatting

### Section Headers

```markdown
## Major Section (h2)

### Subsection (h3)

#### Minor Heading (h4)

##### Rarely Use h5

###### Never Use h6
```

**Rules:**
- h1 only for document title
- h2 for major sections
- h3 for subsections
- Avoid going deeper than h4
- Always include blank lines before and after headers

### Lists

**Unordered Lists:**
```markdown
- First item
- Second item
  - Nested item (2 spaces)
  - Another nested item
- Third item
```

**Ordered Lists:**
```markdown
1. First step
2. Second step
3. Third step
```

**Task Lists:**
```markdown
- [x] Completed task
- [ ] Pending task
- [ ] Another pending task
```

### Emphasis

```markdown
**Bold** for important terms
*Italic* for emphasis
`code` for inline code, commands, file names
~~Strikethrough~~ for deprecated content
```

### Tables

```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |
```

**Rules:**
- Use tables for structured data
- Keep tables simple (max 5 columns)
- Align headers with content
- Use `---` separator row

---

## Code Blocks

### Syntax Highlighting

````markdown
```python
def example():
    return "Always specify language"
```

```bash
echo "Use bash for shell commands"
```

```gdscript
extends Node3D
# Use gdscript for Godot
```

```json
{
  "key": "value"
}
```
````

### File Paths

```markdown
Use `backticks` for file paths: `tools/portal_convert.py`
Use **bold** for emphasis: **File:** `path/to/file.py`
```

### Command Examples

```markdown
# Show command with description
```bash
# This is a comment explaining the command
python3 tools/portal_convert.py --map Kursk
```
```

---

## Cross-References

### Internal Links

```markdown
See [Architecture Doc](./architecture/Multi_Era_Support.md) for details.
Refer to [Section Name](#section-name) in this document.
```

**Rules:**
- Use relative paths
- Provide context: "See X for Y" not just "See X"
- Link liberally to related content
- Test all links

### External Links

```markdown
- [Godot Documentation](https://docs.godotengine.org/en/stable/)
- [BF1942 Modding](https://bfmods.com)
```

**Rules:**
- Always use HTTPS when available
- Include link text that describes destination
- Verify links are current

---

## Admonitions

### Standard Admonitions

Use a **two-line format** with an emoji/bold title on the first line and a "Use:" context line on the second:

```markdown
> ⚠️ **Warning:** Critical information that prevents errors
> **Use:** Safety warnings, breaking changes, destructive operations

> 💡 **Tip:** Helpful suggestion or best practice
> **Use:** Performance tips, shortcuts, recommended approaches

> 📝 **Note:** Additional context or clarification
> **Use:** Extra information, side notes, related facts

> ✅ **Success:** Confirmation or expected outcome
> **Use:** Verification steps, success indicators

> 🚧 **Coming Soon:** Future features or planned improvements
> **Use:** Roadmap items, planned features

> ❌ **Error:** Common errors and solutions
> **Use:** Troubleshooting, common pitfalls

> 🔧 **Advanced:** Expert-level content
> **Use:** Advanced configurations, edge cases

> 🎯 **Example:** Concrete usage example
> **Use:** Practical demonstrations, code samples
```

### Usage

The two-line format provides both immediate information and context for when to use that information:

```markdown
> ⚠️ **Warning:** Download the **STANDARD** version, **NOT** .NET/Mono
> **Use:** Critical setup requirement to avoid installation failures

> 💡 **Tip:** Use `--verbose` flag for detailed output
> **Use:** Debugging conversion issues or understanding pipeline steps

> 📝 **Note:** This structure is from BF1942 v1.6. Earlier versions may differ.
> **Use:** Understanding version-specific differences in file formats
```

---

## Footer Pattern

### Standard Footer

```markdown
---

**Last Updated:** October 2025
**Status:** Current | Deprecated | Reference Only | Beta
**See Also:** [Related Doc](./path.md), [Another Doc](./path.md)
```

### Specialized Footers

**For Guides:**
```markdown
---

**Next Steps:**
1. [Next Guide](./next-guide.md)
2. [Advanced Topics](./advanced.md)

**Last Updated:** October 2025
```

**For Reference Docs:**
```markdown
---

**References:**
- [External Source](https://example.com)
- [Related Spec](./spec.md)

**Last Updated:** October 2025
**Status:** Technical reference - accurate for [Version]
```

---

## File Naming

### Conventions

**Use PascalCase for multi-word docs:**
- `Multi_Era_Support.md` ✅
- `multi-era-support.md` ❌
- `multierasupport.md` ❌

**Use underscores for word separation:**
- `BF1942_Data_Structures.md` ✅
- `BF1942-Data-Structures.md` ❌

**Exception: README files:**
- `README.md` (all caps)
- `CONTRIBUTING.md` (all caps)
- `LICENSE.md` (all caps)

**Descriptive names:**
- `Godot_Setup_Guide.md` ✅ (tells you what it is)
- `Setup.md` ❌ (too vague)

---

## Document Templates

### Architecture Document Template

```markdown
# [Architecture Name]

**Purpose:** [What this architecture document covers]
**Last Updated:** [Month Year]
**Status:** ✅ Implemented | 🚧 In Progress | 📅 Planned
**Complexity:** Low | Medium | High

---

## Table of Contents

[TOC here]

---

## Overview

[High-level description]

## Architecture Design

[Detailed design]

## Implementation

[How it's implemented]

## Examples

[Practical examples]

---

**Last Updated:** [Month Year]
**See Also:** [Related docs]
```

### Setup Guide Template

```markdown
# [Guide Title]

**Purpose:** [What you'll learn]
**Last Updated:** [Month Year]
**Difficulty:** Beginner | Intermediate | Advanced
**Time Required:** ~[X] minutes

---

## Table of Contents

[TOC here]

---

## Prerequisites

- Requirement 1
- Requirement 2

## Installation

### [Platform 1]

[Steps]

### [Platform 2]

[Steps]

## Verification

[How to verify setup]

## Troubleshooting

[Common issues]

---

**Next Steps:**
1. [Next guide](./next.md)

**Last Updated:** [Month Year]
```

### Reference Document Template

```markdown
# [Reference Title]

**Purpose:** [What this reference covers]
**Last Updated:** [Month Year]
**Status:** Technical reference

---

## Table of Contents

[TOC here]

---

## Overview

[Brief introduction]

## [Section 1]

[Content]

## [Section 2]

[Content]

---

**References:**
- [External source 1](url)
- [External source 2](url)

**Last Updated:** [Month Year]
```

---

## Checklist for New Documents

- [ ] Title and header with purpose/status/date
- [ ] Table of contents (if >150 lines)
- [ ] Proper section hierarchy (h1 → h2 → h3)
- [ ] Code blocks with language specified
- [ ] Internal links tested
- [ ] External links use HTTPS
- [ ] Footer with date and status
- [ ] Spell check completed
- [ ] Follows file naming convention
- [ ] Added to docs/README.md if appropriate

---

## Examples from This Project

**Well-Formatted Docs:**
- ✅ `docs/reference/BF1942_Data_Structures.md` - Complete TOC, clear structure
- ✅ `docs/architecture/Multi_Era_Support.md` - Good use of code examples
- ✅ `docs/setup/Godot_Setup_Guide.md` - Clear step-by-step format

**Formatting to Improve:**
- (Will be updated as we standardize)

---

**Last Updated:** October 2025
**Status:** Official Style Guide
**Maintained By:** Project Maintainers

**See Also:**
- [docs/README.md](./README.md) - Documentation hub
- [GitHub Markdown Guide](https://guides.github.com/features/mastering-markdown/)
- [Shields.io](https://shields.io/) - Badge generator
