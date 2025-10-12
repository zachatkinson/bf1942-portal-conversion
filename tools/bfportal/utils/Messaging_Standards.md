# BFPortal Messaging Standards

## Overview

The BFPortal SDK uses a consistent emoji-prefixed messaging pattern for user communication. This provides visual clarity and consistent user experience across all tools.

## Message Categories

### ✅ Success Messages
- **Usage**: Successful operations, confirmations, completions
- **Examples**:
  - `✅ Loaded 733 asset mappings from bf1942_to_portal_mappings.json`
  - `✅ Map parsing complete`
  - `✅ Generated rebased map: Kursk_outskirts.tscn`

### ℹ️  Informational Messages
- **Usage**: Helpful information, alternatives used, skipped items
- **Indentation**: Usually indented with `"  "` (2 spaces) to show subordinate info
- **Examples**:
  - `  ℹ️  Using unrestricted alternative: Oak_Tree_01 for BF1942_Pine`
  - `  ℹ️  Skipping terrain element: Lake_Kursk (water bodies not supported)`
  - `  ℹ️  Using best-guess fallback: Sandbag_Wall for unmapped Fortification_Sand`

### ⚠️  Warning Messages
- **Usage**: Non-critical issues, fallbacks triggered, potential problems
- **Indentation**: Usually indented to show context
- **Examples**:
  - `⚠️  Warning: No bounds provided, using default 2048x2048`
  - `  ⚠️  Mapped asset 'BF1942_Tank' not in catalog, trying fallback`
  - `  ⚠️  Only 2 spawns found for team 1. Portal requires minimum 4.`

### ❌ Error Messages
- **Usage**: Critical failures, exceptions, validation errors
- **Action**: Usually followed by raising an exception
- **Examples**:
  - `❌ Error: Input file not found: Kursk.tscn`
  - `❌ Terrain error: Heightmap dimensions must be square`

### 🔄 Processing Messages
- **Usage**: Ongoing operations, transformations in progress
- **Examples**:
  - `  🔄 Using map-specific fallback: MP_Tungsten_Tree for Kursk_Pine`
  - `🔄 Adjusting heights...`

### Other Emojis
- `📦` - Objects/assets count
- `🔫` - Spawn points
- `🚩` - Capture points
- `📁` - File operations
- `📊` - Statistics/reports
- `📏` - Measurements/dimensions
- `📖` - Reading operations
- `💾` - Saving operations
- `🗺️` - Map/terrain operations

## Code Guidelines

### DO:
```python
# Use emojis for user-facing messages
print(f"✅ Loaded {len(self.mappings)} asset mappings from {mappings_file.name}")

# Indent subordinate information
print(f"  ℹ️  Using alternative: {asset_name}")

# Combine with exceptions for errors
print(f"❌ Error: {error_message}")
raise MappingError(f"Detailed error: {details}")
```

### DON'T:
```python
# Don't mix styles
logger.info("Loaded mappings")  # Inconsistent with emoji pattern
print("Warning:", message)       # Missing emoji prefix

# Don't over-complicate
logging.getLogger(__name__).warning(...)  # Too heavy for CLI tool
```

## Exception Handling

Exceptions should include detailed technical information:

```python
raise MappingError(
    f"Portal asset '{portal_type}' is restricted to "
    f"{portal_asset.level_restrictions} and not available on "
    f"'{context.target_base_map}'. No fallback found. "
    f"BF1942 asset: {source_asset}"
)
```

## Rationale

1. **Visual Clarity**: Emojis provide instant recognition of message type
2. **Simplicity**: No logging configuration needed - direct stdout/stderr
3. **User-Friendly**: CLI tools benefit from immediate visual feedback
4. **Lightweight**: No dependencies on logging frameworks
5. **Consistent**: Same pattern across all modules

## Migration from Logging

If migrating code that uses `logging`:

**Before**:
```python
import logging
logger = logging.getLogger(__name__)

logger.info("Processing...")
logger.warning("Issue detected")
logger.error("Failed")
```

**After**:
```python
print("📊 Processing...")
print("  ⚠️  Issue detected")
print("❌ Failed")
raise SomeError("Detailed error message")
```
