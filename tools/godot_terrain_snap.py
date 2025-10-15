#!/usr/bin/env python3
"""
Godot Terrain Snapping Tool

This script is called by the Godot editor plugin to snap objects to terrain.
It modifies the .tscn file directly, updating Y positions based on terrain raycasting.

Usage:
    python3 godot_terrain_snap.py <path_to_tscn_file>

Returns:
    0 on success
    1 on error
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from bfportal.utils.tscn_utils import TscnParser
from bfportal.terrain.terrain_provider import TerrainProvider


def snap_objects_to_terrain(tscn_path: Path) -> Dict[str, any]:
    """
    Snap all objects in a .tscn file to Portal terrain.

    Args:
        tscn_path: Path to the .tscn scene file

    Returns:
        Dictionary with results:
        {
            "success": bool,
            "total_snapped": int,
            "gameplay_objects": int,
            "static_objects": int,
            "errors": List[str],
            "message": str
        }
    """
    result = {
        "success": False,
        "total_snapped": 0,
        "gameplay_objects": 0,
        "static_objects": 0,
        "errors": [],
        "message": ""
    }

    try:
        # Parse the .tscn file
        parser = TscnParser(tscn_path)
        nodes = parser.parse()

        # Find terrain node to get terrain provider
        terrain_node = None
        for node in nodes:
            if "Terrain" in node.get("name", "") and node.get("parent") == "Static":
                terrain_node = node
                break

        if not terrain_node:
            result["errors"].append("No terrain node found in Static layer")
            result["message"] = "❌ No terrain found in scene"
            return result

        # Determine base map from terrain type
        terrain_type = terrain_node.get("type", "")
        base_map = terrain_type.replace("_Terrain", "") if terrain_type else "MP_Tungsten"

        # Initialize terrain provider
        terrain_provider = TerrainProvider(base_map)

        # Track snapped objects
        gameplay_count = 0
        static_count = 0

        # Snap gameplay objects and their children
        for node in nodes:
            node_name = node.get("name", "")
            parent = node.get("parent", "")

            # Skip Static layer itself
            if node_name == "Static":
                continue

            # Check if gameplay object at root level
            is_gameplay = any(keyword in node_name for keyword in [
                "HQ", "CapturePoint", "VehicleSpawner",
                "StationaryEmplacement", "CombatArea"
            ])

            if is_gameplay and parent == ".":
                # Snap the parent object
                if _snap_node(node, terrain_provider, nodes):
                    gameplay_count += 1

                # Snap all its children (spawn points)
                for child in nodes:
                    if child.get("parent") == node_name:
                        if "Spawn" in child.get("name", ""):
                            if _snap_node(child, terrain_provider, nodes, parent_node=node):
                                gameplay_count += 1

            # Snap static objects in Static layer
            elif parent == "Static" and node_name not in ["Terrain", "Assets"]:
                if _snap_node(node, terrain_provider, nodes):
                    static_count += 1

        # Write updated .tscn file
        parser.write_nodes(nodes, tscn_path)

        result["success"] = True
        result["total_snapped"] = gameplay_count + static_count
        result["gameplay_objects"] = gameplay_count
        result["static_objects"] = static_count
        result["message"] = f"✅ Snapped {result['total_snapped']} objects to terrain!"

    except Exception as e:
        result["errors"].append(str(e))
        result["message"] = f"❌ Error: {str(e)}"

    return result


def _snap_node(
    node: Dict,
    terrain_provider: TerrainProvider,
    all_nodes: List[Dict],
    parent_node: Optional[Dict] = None
) -> bool:
    """
    Snap a single node to terrain by updating its Y position.

    Args:
        node: Node dictionary from TscnParser
        terrain_provider: TerrainProvider instance
        all_nodes: All nodes in the scene (for finding parents)
        parent_node: Parent node if this is a child (for local coords)

    Returns:
        True if snapped successfully, False otherwise
    """
    try:
        # Get node's world position
        transform = node.get("transform")
        if not transform:
            return False

        # Parse transform (4x3 matrix in Godot format)
        # Transform3D(right.x, up.x, forward.x, right.y, up.y, forward.y, right.z, up.z, forward.z, pos.x, pos.y, pos.z)
        parts = transform.split("(")[1].split(")")[0].split(",")
        if len(parts) != 12:
            return False

        # Extract position (last 3 values)
        x = float(parts[9].strip())
        y = float(parts[10].strip())
        z = float(parts[11].strip())

        # If this is a child node, we need to convert to world coordinates
        if parent_node:
            # Get parent's world position
            parent_transform = parent_node.get("transform", "")
            parent_parts = parent_transform.split("(")[1].split(")")[0].split(",")
            parent_x = float(parent_parts[9].strip())
            parent_y = float(parent_parts[10].strip())
            parent_z = float(parent_parts[11].strip())

            # Convert local to world (simplified - assumes no rotation)
            world_x = parent_x + x
            world_y = parent_y + y
            world_z = parent_z + z
        else:
            world_x, world_y, world_z = x, y, z

        # Get terrain height at this XZ position
        terrain_height = terrain_provider.get_height_at_position(world_x, world_z)

        # Calculate new Y position
        if parent_node:
            # For children, update local Y relative to parent
            parent_transform = parent_node.get("transform", "")
            parent_parts = parent_transform.split("(")[1].split(")")[0].split(",")
            parent_y = float(parent_parts[10].strip())
            new_y = terrain_height - parent_y
        else:
            # For root objects, use world Y directly
            new_y = terrain_height

        # Update transform with new Y
        parts[10] = f" {new_y}"
        new_transform = f"Transform3D({', '.join(parts)})"
        node["transform"] = new_transform

        print(f"  ✓ {node['name']}: Y {y:.2f} → {new_y:.2f} (Δ{new_y - y:.2f})")
        return True

    except Exception as e:
        print(f"  ⚠️  {node.get('name', 'Unknown')}: Failed to snap ({str(e)})")
        return False


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 godot_terrain_snap.py <path_to_tscn_file>", file=sys.stderr)
        return 1

    tscn_path = Path(sys.argv[1])

    if not tscn_path.exists():
        print(f"❌ File not found: {tscn_path}", file=sys.stderr)
        return 1

    print(f"🔧 Snapping objects to terrain in: {tscn_path.name}")
    print("=" * 60)

    result = snap_objects_to_terrain(tscn_path)

    print("\n" + "=" * 60)
    print(result["message"])

    if result["errors"]:
        print("\n⚠️  Errors:")
        for error in result["errors"]:
            print(f"  - {error}")

    # Output JSON for Godot to parse
    print("\nJSON_RESULT:", json.dumps(result))

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
