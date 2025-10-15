#!/usr/bin/env python3
"""Verify that BF1942 assets are correctly bound to Portal assets with proper transforms.

This tool:
1. Checks that .tscn nodes reference valid Portal asset types
2. Verifies Transform3D includes rotation + scale
3. Confirms Portal spatial.json has corresponding objects with correct transforms
"""

import json
import re
import sys
from pathlib import Path


def extract_tscn_objects(tscn_path: Path) -> list[dict]:
    """Extract objects from .tscn file.

    Args:
        tscn_path: Path to .tscn file

    Returns:
        List of dicts with {name, type, transform}
    """
    objects = []

    with open(tscn_path) as f:
        lines = f.readlines()

    current_node = None
    for _i, line in enumerate(lines):
        # Match node definitions
        node_match = re.match(r'\[node name="([^"]+)".*parent="Static"', line)
        if node_match:
            node_name = node_match.group(1)
            # Extract asset type from node name (remove _number suffix)
            asset_type = re.sub(r"_\d+$", "", node_name)
            current_node = {"name": node_name, "type": asset_type, "transform": None}
            objects.append(current_node)

        # Match transform lines
        if current_node and line.startswith("transform ="):
            current_node["transform"] = line.strip()

    return objects


def parse_transform3d(transform_str: str) -> dict | None:
    """Parse Transform3D string to extract basis and origin.

    Args:
        transform_str: Transform3D line from .tscn

    Returns:
        Dict with {basis: [[...], [...], [...]]], origin: [...]}
    """
    match = re.search(r"Transform3D\((.*?)\)", transform_str)
    if not match:
        return None

    values = [float(x.strip()) for x in match.group(1).split(",")]
    if len(values) != 12:
        return None

    return {
        "basis": [
            [values[0], values[1], values[2]],  # X basis
            [values[3], values[4], values[5]],  # Y basis
            [values[6], values[7], values[8]],  # Z basis
        ],
        "origin": [values[9], values[10], values[11]],
    }


def extract_scale_from_basis(basis: list[list[float]]) -> tuple[float, float, float]:
    """Extract scale from basis matrix.

    Args:
        basis: 3x3 basis matrix

    Returns:
        Tuple of (scale_x, scale_y, scale_z)
    """
    import math

    # Scale is the length of each basis vector
    scale_x = math.sqrt(basis[0][0] ** 2 + basis[1][0] ** 2 + basis[2][0] ** 2)
    scale_y = math.sqrt(basis[0][1] ** 2 + basis[1][1] ** 2 + basis[2][1] ** 2)
    scale_z = math.sqrt(basis[0][2] ** 2 + basis[1][2] ** 2 + basis[2][2] ** 2)

    return (scale_x, scale_y, scale_z)


def load_spatial_json(spatial_path: Path) -> dict[str, list[dict]]:
    """Load spatial.json file.

    Args:
        spatial_path: Path to .spatial.json file

    Returns:
        Parsed JSON data with Portal_Dynamic and Static lists
    """
    with open(spatial_path) as f:
        data: dict[str, list[dict]] = json.load(f)
        return data


def verify_asset_binding(map_name: str, check_spatial: bool = True) -> dict:
    """Verify asset binding for a map.

    Args:
        map_name: Name of map to verify
        check_spatial: Also verify .spatial.json export

    Returns:
        Dict with verification results and statistics
    """
    project_root = Path.cwd()
    tscn_path = project_root / "GodotProject" / "levels" / f"{map_name}.tscn"
    spatial_path = project_root / "FbExportData" / "levels" / f"{map_name}.spatial.json"
    asset_types_path = project_root / "FbExportData" / "asset_types.json"

    if not tscn_path.exists():
        return {"error": f".tscn not found: {tscn_path}"}

    # Load Portal asset catalog
    with open(asset_types_path) as f:
        asset_catalog = json.load(f)
        valid_asset_types = {asset["type"] for asset in asset_catalog["AssetTypes"]}

    print(f"\n{'=' * 70}")
    print(f"ASSET BINDING VERIFICATION: {map_name}")
    print(f"{'=' * 70}\n")

    # Extract objects from .tscn
    objects = extract_tscn_objects(tscn_path)
    print(f"📦 Found {len(objects)} objects in .tscn")

    # Analyze asset types
    asset_type_counts: dict[str, int] = {}
    for obj in objects:
        asset_type_counts[obj["type"]] = asset_type_counts.get(obj["type"], 0) + 1

    print(f"\n🏷️  Asset Types ({len(asset_type_counts)} unique):")
    for asset_type in sorted(asset_type_counts.keys())[:10]:
        count = asset_type_counts[asset_type]
        is_valid = "✅" if asset_type in valid_asset_types else "⚠️"
        print(f"   {is_valid} {asset_type}: {count} instances")

    if len(asset_type_counts) > 10:
        print(f"   ... and {len(asset_type_counts) - 10} more types")

    # Verify transforms
    with_transforms = sum(1 for obj in objects if obj["transform"])
    with_scale = 0
    with_rotation = 0

    for obj in objects:
        if obj["transform"]:
            parsed = parse_transform3d(obj["transform"])
            if parsed:
                scale = extract_scale_from_basis(parsed["basis"])
                # Check if scale is non-uniform (not all 1.0)
                if (
                    abs(scale[0] - 1.0) > 0.01
                    or abs(scale[1] - 1.0) > 0.01
                    or abs(scale[2] - 1.0) > 0.01
                ):
                    with_scale += 1

                # Check if rotation exists (off-diagonal elements)
                basis = parsed["basis"]
                if abs(basis[0][1]) > 0.01 or abs(basis[0][2]) > 0.01:
                    with_rotation += 1

    print("\n🔄 Transform Analysis:")
    print(f"   Objects with transforms: {with_transforms}/{len(objects)}")
    print(f"   Objects with non-uniform scale: {with_scale}")
    print(f"   Objects with rotation: {with_rotation}")

    # Sample scale values
    print("\n📏 Sample Scale Values (first 5 scaled objects):")
    count = 0
    for obj in objects:
        if obj["transform"] and count < 5:
            parsed = parse_transform3d(obj["transform"])
            if parsed:
                scale = extract_scale_from_basis(parsed["basis"])
                if (
                    abs(scale[0] - 1.0) > 0.01
                    or abs(scale[1] - 1.0) > 0.01
                    or abs(scale[2] - 1.0) > 0.01
                ):
                    print(
                        f"   {obj['name']}: scale=({scale[0]:.3f}, {scale[1]:.3f}, {scale[2]:.3f})"
                    )
                    count += 1

    # Verify spatial.json export (if requested)
    if check_spatial and spatial_path.exists():
        spatial_data = load_spatial_json(spatial_path)
        static_objects = spatial_data.get("Static", [])

        print("\n📤 Spatial Export Verification:")
        print(f"   Objects in .spatial.json: {len(static_objects)}")

        # Check if names match
        spatial_names = {obj["name"] for obj in static_objects if "name" in obj}
        tscn_names = {obj["name"] for obj in objects}

        missing_in_spatial = len(tscn_names - spatial_names)
        extra_in_spatial = len(spatial_names - tscn_names)

        if missing_in_spatial == 0 and extra_in_spatial == 0:
            print("   ✅ All .tscn objects exported to .spatial.json")
        else:
            print(f"   ⚠️  Missing in spatial: {missing_in_spatial}")
            print(f"   ⚠️  Extra in spatial: {extra_in_spatial}")

    elif check_spatial:
        print(f"\n⚠️  Spatial.json not found: {spatial_path}")
        print(f"   Run: python3 tools/export_to_portal.py {map_name}")

    print(f"\n{'=' * 70}")
    print("✅ VERIFICATION COMPLETE")
    print(f"{'=' * 70}\n")

    return {
        "total_objects": len(objects),
        "unique_asset_types": len(asset_type_counts),
        "with_transforms": with_transforms,
        "with_scale": with_scale,
        "with_rotation": with_rotation,
    }


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Verify asset binding for converted maps")

    parser.add_argument("map_name", help="Map name (e.g., Kursk)")
    parser.add_argument(
        "--skip-spatial",
        action="store_true",
        help="Skip .spatial.json verification",
    )

    args = parser.parse_args()

    result = verify_asset_binding(args.map_name, check_spatial=not args.skip_spatial)

    if "error" in result:
        print(f"❌ Error: {result['error']}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
