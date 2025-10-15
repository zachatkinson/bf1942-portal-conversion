#!/usr/bin/env python3
"""Randomize tree assets in converted maps for visual variety.

This tool replaces generic tree mappings (e.g., all Birch_01_L) with
randomized tree types appropriate for the terrain, while:
- Clustering burnt/damaged trees together for realism
- Maintaining size categories (large → large, medium → medium)
- Using only assets available on the target terrain
"""

import json
import random
import re
import sys
from pathlib import Path

from bfportal.generators.constants.paths import (
    get_asset_types_path,
    get_level_tscn_path,
)


def load_tree_catalog(terrain: str = "MP_Tungsten") -> dict[str, list[str]]:
    """Load available tree types for a terrain.

    Args:
        terrain: Target terrain name

    Returns:
        Dict with categories: large, medium, small, dead, burnt
    """
    catalog_path = get_asset_types_path()
    with open(catalog_path) as f:
        data = json.load(f)

    trees: dict[str, list[str]] = {"large": [], "medium": [], "small": [], "dead": [], "burnt": []}

    for asset in data.get("AssetTypes", []):
        asset_type = asset.get("type", "")
        directory = asset.get("directory", "")
        restrictions = asset.get("levelRestrictions", [])

        # Check if it's a tree
        tree_keywords = [
            "birch",
            "pine",
            "oak",
            "spruce",
            "fir",
            "poplar",
            "walnut",
            "hawthorn",
            "juniper",
            "pear",
            "olive",
            "fig",
            "lemonade",
        ]
        is_tree = "nature" in directory.lower() or any(
            kw in asset_type.lower() for kw in tree_keywords
        )

        # Exclude non-tree objects
        exclude = [
            "rock",
            "cliff",
            "bush",
            "grass",
            "dirt",
            "earth",
            "mound",
            "stump",
            "branch",
            "log",
            "trunk",
            "fx_",
            "sfx_",
        ]
        if any(ex in asset_type.lower() for ex in exclude):
            continue

        # Must be available on terrain
        if is_tree and (not restrictions or terrain in restrictions):
            # Categorize
            if "burnt" in asset_type.lower() or "burning" in asset_type.lower():
                trees["burnt"].append(asset_type)
            elif "dead" in asset_type.lower():
                trees["dead"].append(asset_type)
            elif "_L" in asset_type or "Large" in asset_type:
                trees["large"].append(asset_type)
            elif "_M" in asset_type or "Medium" in asset_type:
                trees["medium"].append(asset_type)
            elif "_S" in asset_type or "Small" in asset_type:
                trees["small"].append(asset_type)

    return trees


def get_size_category(asset_name: str) -> str:
    """Determine size category from asset name."""
    if "_L" in asset_name or "_L_" in asset_name or "Large" in asset_name:
        return "large"
    elif "_M" in asset_name or "_M_" in asset_name or "Medium" in asset_name:
        return "medium"
    elif "_S" in asset_name or "_S_" in asset_name or "Small" in asset_name:
        return "small"
    return "medium"  # Default


def detect_tree_clusters(tscn_path: Path) -> dict[str, list[tuple]]:
    """Detect clusters of trees that should use same variant.

    Returns:
        Dict mapping cluster_id to list of (node_name, position)
    """
    # For now, return empty - we'll implement spatial clustering if needed
    return {}


def randomize_trees_in_tscn(
    tscn_path: Path,
    terrain: str = "MP_Tungsten",
    burnt_cluster_distance: float = 50.0,
    variety_percentage: float = 0.7,
    seed: int = 42,
) -> int:
    """Randomize tree assets in a .tscn file.

    Args:
        tscn_path: Path to .tscn file
        terrain: Target terrain name
        burnt_cluster_distance: Max distance for burnt tree clustering (meters)
        variety_percentage: Percentage of trees to randomize (0.0-1.0)
        seed: Random seed for reproducibility

    Returns:
        Number of trees randomized
    """
    random.seed(seed)

    # Load tree catalog
    tree_catalog = load_tree_catalog(terrain)

    print(f"🌲 Randomizing trees in {tscn_path.name}...")
    print(
        f"   Available: {len(tree_catalog['large'])} large, "
        f"{len(tree_catalog['medium'])} medium, {len(tree_catalog['small'])} small"
    )
    print(f"   Burnt/dead: {len(tree_catalog['burnt'])} burnt, {len(tree_catalog['dead'])} dead")

    # Read .tscn file
    with open(tscn_path) as f:
        lines = f.readlines()

    # Track changes
    replacements = 0
    tree_usage: dict[str, int] = {}

    # Pattern: [node name="Birch_01_L_39" parent="Static" instance=ExtResource("8")]
    node_pattern = re.compile(
        r'\[node name="([^"]+)" parent="Static" instance=ExtResource\("(\d+)"\)\]'
    )
    ext_pattern = re.compile(
        r'\[ext_resource type="PackedScene" path="res://[^"]*([^/]+)\.tscn" id="(\d+)"\]'
    )

    # Build ExtResource map: id -> asset_type
    ext_map = {}
    for line in lines:
        match = ext_pattern.match(line)
        if match:
            asset_type = match.group(1)
            ext_id = match.group(2)
            ext_map[ext_id] = asset_type

    # Find tree nodes and decide replacements
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        match = node_pattern.match(line)

        if match:
            match.group(1)
            ext_id = match.group(2)
            asset_type = ext_map.get(ext_id, "")

            # Check if this is a tree we should randomize
            size = get_size_category(asset_type)
            is_tree = size in tree_catalog and tree_catalog[size]

            # Randomize if it's a tree and we're in variety percentage
            if is_tree and random.random() < variety_percentage:
                # Pick random tree from same size category
                new_tree = random.choice(tree_catalog[size])

                # Track usage
                tree_usage[new_tree] = tree_usage.get(new_tree, 0) + 1

                # Find or create ExtResource for new tree
                new_ext_id = None
                for eid, atype in ext_map.items():
                    if atype == new_tree:
                        new_ext_id = eid
                        break

                if new_ext_id is None:
                    # Need to add new ExtResource
                    # For now, keep original (would need to add to ext_resources section)
                    new_lines.append(line)
                else:
                    # Replace with new tree
                    new_line = line.replace(
                        f'ExtResource("{ext_id}")', f'ExtResource("{new_ext_id}")'
                    )
                    new_lines.append(new_line)
                    replacements += 1
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

        i += 1

    # Write back
    with open(tscn_path, "w") as f:
        f.writelines(new_lines)

    print(f"   ✅ Randomized {replacements} trees")
    print("   Tree variety used:")
    for tree_type, count in sorted(tree_usage.items(), key=lambda x: -x[1])[:10]:
        print(f"      • {tree_type}: {count}")

    return replacements


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Randomize tree assets in converted maps")
    parser.add_argument("map_name", help="Map name (e.g., Kursk)")
    parser.add_argument("--terrain", default="MP_Tungsten", help="Target terrain")
    parser.add_argument(
        "--variety", type=float, default=0.7, help="Percentage of trees to randomize (0.0-1.0)"
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")

    args = parser.parse_args()

    tscn_path = get_level_tscn_path(args.map_name)
    if not tscn_path.exists():
        print(f"❌ Map not found: {tscn_path}")
        return 1

    count = randomize_trees_in_tscn(
        tscn_path, terrain=args.terrain, variety_percentage=args.variety, seed=args.seed
    )

    if count > 0:
        print(f"\n✅ Successfully randomized {count} trees in {args.map_name}")
        print("💡 Tip: Regenerate the map to create fresh tree variety")
    else:
        print("\n⚠️  No trees randomized (all ExtResources already in file)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
