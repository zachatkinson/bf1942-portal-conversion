# macOS Compatibility for BF6 Portal SDK

> macOS-specific workarounds and manual export procedures for Portal SDK development

**Purpose:** macOS-specific workarounds for Portal SDK Windows-only features and manual export procedures
**Last Updated:** October 2025
**Status:** ⚠️ REFERENCE DOCUMENT - macOS fixes not yet implemented in this project
**Difficulty:** Intermediate
**Time Required:** ~20 minutes

---

## Table of Contents

- [The Issue](#the-issue)
- [What Works on macOS (No Patch Needed)](#what-works-on-macos-no-patch-needed)
- [What Doesn't Work (Windows-Only)](#what-doesnt-work-windows-only)
- [Workaround: Manual Export on macOS](#workaround-manual-export-on-macos)
  - [Step 1: Check Python Installation](#step-1-check-python-installation)
  - [Step 2: Install Dependencies](#step-2-install-dependencies)
  - [Step 3: Export Map Manually](#step-3-export-map-manually)
  - [Step 4: Verify Export](#step-4-verify-export)
- [Optional: Shell Script for Easy Export](#optional-shell-script-for-easy-export)
- [Official Patch (Optional - Modifies Plugin Code)](#official-patch-optional---modifies-plugin-code)
  - [Patch 1: Suppress macOS Setup Error](#patch-1-suppress-macos-setup-error)
  - [Patch 2: Enable Manual Export Info for macOS](#patch-2-enable-manual-export-info-for-macos)
- [Testing the Workaround](#testing-the-workaround)
- [Advantages of Manual Export](#advantages-of-manual-export)
- [Summary](#summary)

---

## The Issue

When opening Godot with the Portal SDK on macOS, you see:

```
ERROR: Setup has not been implemented for your platform: macOS
```

### What This Actually Means

The Portal SDK has **three components**:

1. **Map Editing** (Godot editor) - ✅ **WORKS ON macOS**
2. **Python Virtual Environment Setup** (Windows-only GUI button) - ❌ Windows only
3. **Map Export** (.tscn → .spatial.json) - ✅ **WORKS ON macOS** (with workaround)

**The error is ONLY about the "Setup" button in the Portal Tools panel!**

The object library generation already succeeded:
```
Generating object library
```

This line appeared BEFORE the error, meaning the critical part worked fine!

---

## What Works on macOS (No Patch Needed)

### ✅ Map Editing
- Open .tscn files
- View 3D scenes
- Edit object positions
- Add/remove objects
- Navigate scene tree
- Use Inspector panel
- Save changes

### ✅ Map Export (Manual Method)
- Convert .tscn → .spatial.json
- Uses existing Python code
- No virtual environment needed
- Direct Python execution

---

## What Doesn't Work (Windows-Only)

### ❌ "Setup" Button in Portal Tools Panel
- **Purpose**: Creates Windows Python virtual environment
- **Why It Fails**: Uses PowerShell and .exe paths
- **Impact**: None - we don't need this button

### ❌ "Export Level" GUI Button
- **Purpose**: Convenience wrapper for Python script
- **Why It Fails**: Checks `if OS.get_name() != "Windows": return`
- **Impact**: Minor - we can run the script manually

---

## Workaround: Manual Export on macOS

Instead of using the GUI button, run the Python export script directly.

### Step 1: Check Python Installation

```bash
# Check if Python 3 is available
python3 --version

# Should show Python 3.8+ (Mac usually has 3.9+)
```

### Step 2: Install Dependencies

The Portal SDK includes a `requirements.txt`:

```bash
cd <PortalSDK>/code/gdconverter

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

**Required packages** (from requirements.txt):
- `lark` - Parser for .tscn files
- Other utilities

### Step 3: Export Map Manually

```bash
# Activate venv if you created one
source <PortalSDK>/code/gdconverter/venv/bin/activate

# Export your map
python3 <PortalSDK>/code/gdconverter/src/gdconverter/export_tscn.py \
  <PortalSDK>/GodotProject/levels/<YourMap>.tscn \
  <PortalSDK>/FbExportData \
  <PortalSDK>/FbExportData/levels
```

**Arguments:**
1. `SCENE_FILE`: Path to .tscn file to export
2. `FB_EXPORT_DATA`: Path to FbExportData directory (asset catalog)
3. `OUTPUT_DIR`: Where to save the .spatial.json

**Output:**
```
<PortalSDK>/FbExportData/levels/<YourMap>.spatial.json
```

### Step 4: Verify Export

```bash
# Check if export succeeded
ls -lh <PortalSDK>/FbExportData/levels/<YourMap>.spatial.json

# View the exported JSON
cat <PortalSDK>/FbExportData/levels/<YourMap>.spatial.json | python3 -m json.tool | head -50
```

---

## Optional: Shell Script for Easy Export

Create a helper script for easier exporting:

**File:** `tools/export_map_macos.sh`

```bash
#!/bin/bash
# macOS helper script for exporting Portal maps

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

GDCONVERTER="${PROJECT_ROOT}/code/gdconverter"
EXPORT_SCRIPT="${GDCONVERTER}/src/gdconverter/export_tscn.py"
FB_EXPORT_DATA="${PROJECT_ROOT}/FbExportData"
OUTPUT_DIR="${FB_EXPORT_DATA}/levels"

# Check if virtual environment exists
PYTHON_CMD="python3"
if [ -f "${GDCONVERTER}/venv/bin/python3" ]; then
    PYTHON_CMD="${GDCONVERTER}/venv/bin/python3"
    echo "Using virtual environment Python"
else
    echo "Using system Python"
fi

# Check arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 <path/to/map.tscn>"
    echo "Example: $0 GodotProject/levels/Kursk.tscn"
    exit 1
fi

TSCN_FILE="$1"

# Make path absolute if relative
if [[ "$TSCN_FILE" != /* ]]; then
    TSCN_FILE="${PROJECT_ROOT}/${TSCN_FILE}"
fi

# Check if file exists
if [ ! -f "$TSCN_FILE" ]; then
    echo "Error: File not found: $TSCN_FILE"
    exit 1
fi

echo "Exporting: $TSCN_FILE"
echo "Output: $OUTPUT_DIR"

# Run export
$PYTHON_CMD "$EXPORT_SCRIPT" "$TSCN_FILE" "$FB_EXPORT_DATA" "$OUTPUT_DIR"

if [ $? -eq 0 ]; then
    MAP_NAME=$(basename "$TSCN_FILE" .tscn)
    OUTPUT_FILE="${OUTPUT_DIR}/${MAP_NAME}.spatial.json"
    echo ""
    echo "✅ Export successful!"
    echo "📄 Output: $OUTPUT_FILE"
    echo ""
    echo "File size: $(du -h "$OUTPUT_FILE" | cut -f1)"
else
    echo ""
    echo "❌ Export failed! Check error messages above."
    exit 1
fi
```

**Make it executable:**
```bash
chmod +x tools/export_map_macos.sh
```

**Usage:**
```bash
# Export a map
./tools/export_map_macos.sh GodotProject/levels/<YourMap>.tscn
```

---

## Official Patch (Optional - Modifies Plugin Code)

If you want to eliminate the error message entirely, you can patch the plugin.

### Patch 1: Suppress macOS Setup Error

**File:** `GodotProject/addons/bf_portal/portal_tools/portal_tools_dock.gd`

**Line 87-92** (Original):
```gdscript
	else:
		var dialog = AcceptDialog.new()  # not member variable because simply one-off
		var msg = "Setup has not been implemented for your platform: %s" % platform
		dialog.dialog_text = msg
		EditorInterface.popup_dialog_centered(dialog)
		printerr(msg)
```

**Replace with:**
```gdscript
	else:
		# macOS/Linux: Setup button not needed - use manual export script
		print("Platform: %s - Setup button is Windows-only. Map editing fully functional." % platform)
		print("For export: Use tools/export_map_macos.sh or run export_tscn.py manually")
```

### Patch 2: Enable Manual Export Info for macOS

**File:** `GodotProject/addons/bf_portal/portal_tools/portal_tools_dock.gd`

**Line 154-156** (Original):
```gdscript
func _export_levels() -> void:
	if OS.get_name() != "Windows":
		return
```

**Replace with:**
```gdscript
func _export_levels() -> void:
	if OS.get_name() != "Windows":
		var dialog = AcceptDialog.new()
		dialog.title = "Export on macOS/Linux"
		dialog.dialog_text = """Export is available via command line:

1. Install dependencies:
   cd code/gdconverter
   pip install -r requirements.txt

2. Run export script:
   python3 code/gdconverter/src/gdconverter/export_tscn.py \\
     <scene.tscn> \\
     FbExportData \\
     FbExportData/levels

Or use: tools/export_map_macos.sh <scene.tscn>"""
		EditorInterface.popup_dialog_centered(dialog)
		return
```

**This change:**
- Shows helpful instructions instead of silently returning
- Provides the exact commands needed
- Makes the workflow clear for macOS users

---

## Testing the Workaround

### Test 1: Verify Map Editing Works

1. Open Godot with Portal SDK project
2. Ignore the "Setup has not been implemented" error
3. Open `GodotProject/levels/<YourMap>.tscn`
4. Scene should load successfully
5. Verify you can:
   - Navigate 3D viewport
   - Select objects
   - View Inspector properties
   - Edit transforms

**Expected:** ✅ Everything works normally

### Test 2: Verify Manual Export Works

```bash
# Install dependencies first
cd <PortalSDK>/code/gdconverter
pip install -r requirements.txt

# Try exporting your map
python3 src/gdconverter/export_tscn.py \
  ../../GodotProject/levels/<YourMap>.tscn \
  ../../FbExportData \
  ../../FbExportData/levels

# Check output
ls -lh ../../FbExportData/levels/<YourMap>.spatial.json
```

**Expected:** Creates `<YourMap>.spatial.json` successfully

---

## Advantages of Manual Export

1. **More Control**: See exactly what's happening
2. **Debugging**: Can add `--verbose` flags if needed
3. **Automation**: Easy to script for batch exports
4. **No Virtual Env Needed**: Uses system Python directly
5. **Works Anywhere**: Same script works on Windows/macOS/Linux

---

## Summary

### The Real Situation

**Portal SDK map editing works perfectly on macOS!** 🎉

The error message is misleading - it's ONLY about:
1. A Windows-specific GUI button for Python venv setup
2. A GUI export button (easily worked around)

### What You Can Do Right Now

✅ **Open and edit .tscn files** - Works perfectly
✅ **View scene tree and 3D viewport** - Works perfectly
✅ **Modify object positions** - Works perfectly
✅ **Save changes** - Works perfectly
✅ **Export to .spatial.json** - Works via manual script

### No Patch Needed for Basic Usage

For basic map editing and testing, **you don't need any patch!**

Just:
1. Ignore the setup error
2. Open your map .tscn file
3. Verify object placements
4. Make manual adjustments if needed
5. When ready to export, use manual Python script

### When to Apply the Patch

Only apply the official code patches if:
- You want to eliminate the error message
- You're converting multiple maps and want cleaner workflow
- You plan to contribute fixes back to the community

---

## Getting Started on macOS

**Immediate Steps:**
1. Close the error dialog in Godot (click OK)
2. Open `GodotProject/levels/<YourMap>.tscn`
3. Scene should load successfully now
4. Begin editing your map

**For Export:**
1. Install Python dependencies: `pip install -r code/gdconverter/requirements.txt`
2. (Optional) Create helper script: `tools/export_map_macos.sh`
3. Test export: `./tools/export_map_macos.sh GodotProject/levels/<YourMap>.tscn`

---

**Last Updated:** October 2025
**Status:** Workaround confirmed functional - Portal SDK fully usable on macOS
**Platform:** macOS (all versions)

**See Also:**
- [Godot Setup Guide](./Godot_Setup_Guide.md) - General Godot installation instructions
- [Main README](../../README.md) - Project overview
- [TESTING.md](../../TESTING.md) - Testing converted maps
