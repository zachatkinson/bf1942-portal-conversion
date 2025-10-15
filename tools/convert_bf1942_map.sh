#!/bin/bash
#
# Complete BF1942 to Portal conversion pipeline wrapper.
#
# This script orchestrates the full conversion workflow:
# 1. portal_convert.py  - Convert BF1942 .con to .tscn with height adjustment
# 2. terrain_snap.py    - Post-process .tscn for precision terrain placement
# 3. export_to_portal.py - Export .tscn to .spatial.json and experience.json
#
# Usage:
#   bash tools/convert_bf1942_map.sh Kursk MP_Tungsten
#
# Arguments:
#   $1 - Map name (e.g., Kursk, El_Alamein)
#   $2 - Base terrain (e.g., MP_Tungsten, MP_Outskirts)
#
# Best Practices (CLAUDE.md):
# - Modular design: Each tool has single responsibility
# - Pipeline orchestration: This wrapper coordinates the workflow
# - Error handling: Stops on first failure
# - Clear output: Shows each step's progress

set -e

MAP_NAME="${1:-Kursk}"
BASE_TERRAIN="${2:-MP_Tungsten}"

echo "======================================================================="
echo "BF1942 TO PORTAL CONVERSION PIPELINE"
echo "======================================================================="
echo "Map: $MAP_NAME"
echo "Base Terrain: $BASE_TERRAIN"
echo ""

# Step 1: Convert BF1942 to .tscn
echo "Step 1/3: Converting BF1942 data to Godot .tscn..."
echo "-----------------------------------------------------------------------"
python3 tools/portal_convert.py --map "$MAP_NAME" --base-terrain "$BASE_TERRAIN"
echo ""

# Step 2: Precision terrain snap
echo "Step 2/3: Snapping objects to terrain surface..."
echo "-----------------------------------------------------------------------"
python3 tools/terrain_snap.py --map "$MAP_NAME" --terrain "$BASE_TERRAIN"
echo ""

# Step 3: Export to Portal format
echo "Step 3/3: Exporting to Portal format..."
echo "-----------------------------------------------------------------------"
python3 tools/export_to_portal.py "$MAP_NAME"
echo ""

echo "======================================================================="
echo "✅ COMPLETE! Pipeline finished successfully"
echo "======================================================================="
echo ""
echo "Output files:"
echo "  - GodotProject/levels/$MAP_NAME.tscn (Godot scene)"
echo "  - FbExportData/levels/$MAP_NAME.spatial.json (Portal spatial data)"
echo "  - experiences/${MAP_NAME}_Experience.json (Portal experience)"
echo ""
echo "Next steps:"
echo "  1. Open Godot and verify: GodotProject/levels/$MAP_NAME.tscn"
echo "  2. Import to Portal: experiences/${MAP_NAME}_Experience.json"
echo "  3. Test in-game!"
echo ""
