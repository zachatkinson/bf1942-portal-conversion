#!/bin/bash
# Export a Godot .tscn map to complete Portal experience format
#
# Usage:
#   ./tools/export_map.sh <map_name> [options]
#
# Examples:
#   ./tools/export_map.sh Kursk
#   ./tools/export_map.sh Kursk --base-map MP_Outskirts --max-players 64
#
# This script is a wrapper around export_to_portal.py which:
# 1. Exports .tscn to .spatial.json
# 2. Creates complete Portal experience file ready for import

set -e  # Exit on error

# Validate arguments
if [ $# -ne 1 ]; then
    echo "Error: Map name required"
    echo "Usage: $0 <map_name>"
    echo "Example: $0 Kursk"
    exit 1
fi

MAP_NAME=$1
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Define paths
TSCN_PATH="$PROJECT_ROOT/GodotProject/levels/${MAP_NAME}.tscn"
ASSET_DIR="$PROJECT_ROOT/FbExportData"
OUTPUT_DIR="$PROJECT_ROOT/FbExportData/levels"
EXPORT_SCRIPT="$PROJECT_ROOT/code/gdconverter/src/gdconverter/export_tscn.py"

# Validate input file exists
if [ ! -f "$TSCN_PATH" ]; then
    echo "Error: Map file not found: $TSCN_PATH"
    echo "Available maps:"
    ls -1 "$PROJECT_ROOT/GodotProject/levels/"*.tscn 2>/dev/null | xargs -n1 basename | sed 's/.tscn$//' || echo "  (none found)"
    exit 1
fi

# Validate export script exists
if [ ! -f "$EXPORT_SCRIPT" ]; then
    echo "Error: Export script not found: $EXPORT_SCRIPT"
    exit 1
fi

# Validate asset directory exists
if [ ! -d "$ASSET_DIR" ]; then
    echo "Error: Asset directory not found: $ASSET_DIR"
    exit 1
fi

# Create output directory if needed
mkdir -p "$OUTPUT_DIR"

echo "Exporting map: $MAP_NAME"
echo "  Input:  $TSCN_PATH"
echo "  Output: $OUTPUT_DIR/${MAP_NAME}.spatial.json"
echo ""

# Run the export
python3 "$EXPORT_SCRIPT" \
    "$TSCN_PATH" \
    "$ASSET_DIR" \
    "$OUTPUT_DIR"

# Verify output was created
OUTPUT_FILE="$OUTPUT_DIR/${MAP_NAME}.spatial.json"
if [ -f "$OUTPUT_FILE" ]; then
    FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
    echo ""
    echo "✅ Export successful!"
    echo "   File: $OUTPUT_FILE"
    echo "   Size: $FILE_SIZE"
    echo ""
    echo "Next steps:"
    echo "  1. Open Battlefield Portal web builder"
    echo "  2. Import $OUTPUT_FILE"
    echo "  3. Test your map in-game!"
else
    echo ""
    echo "❌ Export failed - output file not created"
    exit 1
fi
