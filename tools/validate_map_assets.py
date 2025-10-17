#!/usr/bin/env python3
"""Validate map assets for level restrictions and terrain bounds.

This tool checks:
1. Assets that violate levelRestrictions for the target terrain
2. Objects positioned outside terrain mesh bounds
"""

import re
import sys
from pathlib import Path

from bfportal.generators.constants.paths import (
    get_level_tscn_path,
    get_terrain_glb_path,
)
from bfportal.validators import AssetCatalog


def parse_tscn_objects(tscn_path: Path) -> list[dict]:
    """Parse objects from .tscn file."""
    objects = []

    with open(tscn_path) as f:
        lines = f.readlines()

    current_node = None
    for i, line in enumerate(lines):
        # Match static object nodes
        node_match = re.match(
            r'\[node name="([^"]+)" parent="Static"(?:.*instance=ExtResource\("(\d+)"\))?', line
        )
        if node_match:
            node_name = node_match.group(1)
            ext_id = node_match.group(2)
            # Extract asset type (remove _number suffix)
            asset_type = re.sub(r"_\d+$", "", node_name)
            current_node = {
                "name": node_name,
                "asset_type": asset_type,
                "ext_id": ext_id,
                "transform": None,
                "line": i + 1,
            }
            objects.append(current_node)

        # Match transform line
        if current_node and line.startswith("transform ="):
            # Parse Transform3D to extract position
            match = re.search(r"Transform3D\((.*?)\)", line)
            if match:
                values = [float(x.strip()) for x in match.group(1).split(",")]
                if len(values) == 12:
                    current_node["transform"] = {
                        "x": values[9],
                        "y": values[10],
                        "z": values[11],
                    }

    return objects


def load_ext_resources(tscn_path: Path) -> dict[str, str]:
    """Load ExtResource mappings from .tscn file."""
    ext_resources = {}

    with open(tscn_path) as f:
        for line in f:
            # [ext_resource type="PackedScene" path="res://..." id="7"]
            match = re.match(
                r'\[ext_resource type="PackedScene" path="res://([^"]+)" id="(\d+)"\]', line
            )
            if match:
                path = match.group(1)
                ext_id = match.group(2)
                # Extract asset type from path (filename without .tscn)
                asset_type = Path(path).stem
                ext_resources[ext_id] = asset_type

    return ext_resources


def get_terrain_bounds(terrain_name: str) -> tuple[float, float, float, float] | None:
    """Get terrain bounds from GLB mesh.

    Returns:
        Tuple of (min_x, max_x, min_z, max_z) or None if mesh not found
    """
    # Import here to avoid loading at module level
    from bfportal.terrain.terrain_provider import MeshTerrainProvider

    mesh_path = get_terrain_glb_path(terrain_name)
    if not mesh_path.exists():
        print(f"⚠️  Terrain mesh not found: {mesh_path}")
        return None

    # Terrain size doesn't matter for bounds checking
    provider = MeshTerrainProvider(mesh_path, (2048, 2048))

    min_x = provider.vertices[:, 0].min()
    max_x = provider.vertices[:, 0].max()
    min_z = provider.vertices[:, 2].min()
    max_z = provider.vertices[:, 2].max()

    return (min_x, max_x, min_z, max_z)


def validate_map_assets(map_name: str, terrain_name: str) -> dict:
    """Validate map assets for restrictions and bounds.

    Args:
        map_name: Map name (e.g., "Kursk")
        terrain_name: Portal terrain name (e.g., "MP_Tungsten")

    Returns:
        Dict with validation results
    """
    tscn_path = get_level_tscn_path(map_name)

    if not tscn_path.exists():
        return {"error": f".tscn not found: {tscn_path}"}

    print(f"\n{'=' * 70}")
    print(f"MAP ASSET VALIDATION: {map_name} on {terrain_name}")
    print(f"{'=' * 70}\n")

    # Load asset catalog and objects using shared DRY utilities
    catalog = AssetCatalog()
    load_ext_resources(tscn_path)
    objects = parse_tscn_objects(tscn_path)

    print(f"📦 Found {len(objects)} static objects in .tscn")
    print(f"📖 Loaded {catalog.get_asset_count()} assets from catalog")
    print()

    # Check level restrictions
    print("🔒 Checking Level Restrictions...")
    print("-" * 70)

    restricted_assets = {}
    for obj in objects:
        asset_type = obj["asset_type"]

        # Use shared AssetCatalog methods (DRY principle)
        if catalog.has_asset(asset_type):
            if catalog.has_level_restrictions(asset_type):
                if not catalog.is_allowed_on_map(asset_type, terrain_name):
                    restrictions = catalog.get_level_restrictions(asset_type)
                    if asset_type not in restricted_assets:
                        restricted_assets[asset_type] = {
                            "count": 0,
                            "allowed_maps": restrictions,
                        }
                    restricted_assets[asset_type]["count"] += 1

    if restricted_assets:
        print(f"❌ Found {len(restricted_assets)} asset types with level restrictions violated:\n")
        for asset_type, info in sorted(restricted_assets.items()):
            count = info["count"]
            allowed = ", ".join(info["allowed_maps"][:3])
            if len(info["allowed_maps"]) > 3:
                allowed += f" (+{len(info['allowed_maps']) - 3} more)"
            print(f"   • {asset_type}: {count} instances")
            print(f"     Allowed on: {allowed}")
            print()
    else:
        print("✅ No level restriction violations found")

    print()

    # Check terrain bounds
    print("🗺️  Checking Terrain Bounds...")
    print("-" * 70)

    bounds = get_terrain_bounds(terrain_name)
    if bounds:
        min_x, max_x, min_z, max_z = bounds
        print(f"Terrain bounds: X[{min_x:.1f}, {max_x:.1f}] Z[{min_z:.1f}, {max_z:.1f}]")
        print()

        out_of_bounds = []
        for obj in objects:
            if obj["transform"]:
                x = obj["transform"]["x"]
                z = obj["transform"]["z"]

                if x < min_x or x > max_x or z < min_z or z > max_z:
                    out_of_bounds.append(
                        {
                            "name": obj["name"],
                            "asset_type": obj["asset_type"],
                            "position": (x, z),
                            "line": obj["line"],
                        }
                    )

        if out_of_bounds:
            print(f"❌ Found {len(out_of_bounds)} objects outside terrain bounds:\n")

            # Group by asset type
            by_type: dict[str, list[dict]] = {}
            for obj in out_of_bounds:
                asset_type = obj["asset_type"]
                if asset_type not in by_type:
                    by_type[asset_type] = []
                by_type[asset_type].append(obj)

            for asset_type, objs in sorted(by_type.items()):
                print(f"   • {asset_type}: {len(objs)} instances")
                # Show first few examples
                for obj in objs[:3]:
                    x, z = obj["position"]
                    print(f"     - {obj['name']} at ({x:.1f}, {z:.1f}) [line {obj['line']}]")
                if len(objs) > 3:
                    print(f"     ... and {len(objs) - 3} more")
                print()
        else:
            print("✅ All objects within terrain bounds")

    print(f"{'=' * 70}")
    print("VALIDATION COMPLETE")
    print(f"{'=' * 70}\n")

    return {
        "total_objects": len(objects),
        "restricted_violations": len(restricted_assets),
        "out_of_bounds": len(out_of_bounds) if bounds else 0,
    }


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate map assets for restrictions and bounds")
    parser.add_argument("map_name", help="Map name (e.g., Kursk)")
    parser.add_argument("--terrain", default="MP_Tungsten", help="Portal terrain name")

    args = parser.parse_args()

    result = validate_map_assets(args.map_name, args.terrain)

    if "error" in result:
        print(f"❌ Error: {result['error']}", file=sys.stderr)
        return 1

    # Exit with error if violations found
    if result["restricted_violations"] > 0 or result["out_of_bounds"] > 0:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
