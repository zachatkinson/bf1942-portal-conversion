#!/usr/bin/env python3
"""Auto-generate map-specific fallbacks for tree assets.

This tool analyzes Portal asset catalog and automatically generates
fallback mappings for trees based on their level restrictions.

DRY: Single source of truth for fallback generation logic
SOLID: Single Responsibility - only generates fallbacks, doesn't modify other mappings
"""

import json
from pathlib import Path
from typing import Any


def get_trees_by_map(portal_assets: list[dict]) -> dict[str, list[str]]:
    """Build map-to-trees lookup table.

    Args:
        portal_assets: List of Portal asset definitions

    Returns:
        Dict mapping map name to list of available tree types
    """
    # Tree keywords to identify tree assets
    tree_keywords = [
        "birch",
        "pine",
        "spruce",
        "oak",
        "juniper",
        "poplar",
        "hawthorn",
        "fig",
        "pear",
        "walnut",
    ]

    map_trees: dict[str, list[str]] = {}

    for asset in portal_assets:
        asset_type = asset["type"]
        asset_lower = asset_type.lower()

        # Check if this is a tree asset
        if not any(keyword in asset_lower for keyword in tree_keywords):
            continue

        restrictions = asset.get("levelRestrictions", [])

        if not restrictions:
            # Unrestricted tree - available on ALL maps
            # Add to every map we know about
            for map_name in [
                "MP_Tungsten",
                "MP_Aftermath",
                "MP_Dumbo",
                "MP_Battery",
                "MP_FireStorm",
                "MP_Limestone",
                "MP_Capstone",
                "MP_Outskirts",
                "MP_Abbasid",
            ]:
                if map_name not in map_trees:
                    map_trees[map_name] = []
                map_trees[map_name].append(asset_type)
        else:
            # Restricted tree - only available on specified maps
            for map_name in restrictions:
                if map_name not in map_trees:
                    map_trees[map_name] = []
                map_trees[map_name].append(asset_type)

    return map_trees


def generate_fallback_for_mapping(
    mapping: dict[str, Any], map_trees: dict[str, list[str]], variety_pool: list[str]
) -> dict[str, str]:
    """Generate map-specific fallbacks for a tree mapping.

    Args:
        mapping: Tree mapping entry from bf1942_to_portal_mappings.json
        map_trees: Map-to-trees lookup (from get_trees_by_map)
        variety_pool: List of tree types to use for variety

    Returns:
        Dict mapping map name to fallback tree type

    Strategy:
        1. For each map, check which trees from variety_pool are available
        2. Use first available tree from variety_pool as fallback
        3. If no variety_pool trees available, use any available tree
    """
    fallbacks: dict[str, str] = {}

    for map_name, available_trees in map_trees.items():
        # Try to use a tree from variety_pool first (maintains variety)
        for tree in variety_pool:
            if tree in available_trees:
                fallbacks[map_name] = tree
                break
        else:
            # No variety_pool tree available - use first available tree
            if available_trees:
                fallbacks[map_name] = available_trees[0]

    return fallbacks


def main():
    """Generate map-specific fallbacks for all tree assets."""
    project_root = Path(__file__).parent.parent
    mappings_path = project_root / "tools" / "asset_audit" / "bf1942_to_portal_mappings.json"
    portal_assets_path = project_root / "FbExportData" / "asset_types.json"

    # Load Portal asset catalog
    print("📂 Loading Portal asset catalog...")
    with open(portal_assets_path) as f:
        portal_data = json.load(f)
    portal_assets = portal_data["AssetTypes"]

    # Build map-to-trees lookup
    print("🌳 Building map-to-trees lookup table...")
    map_trees = get_trees_by_map(portal_assets)

    for map_name, trees in map_trees.items():
        print(f"  {map_name}: {len(trees)} trees")

    # Load BF1942 mappings
    print("\n📖 Loading BF1942 mappings...")
    with open(mappings_path) as f:
        mappings = json.load(f)

    # Find all tree mappings and add fallbacks
    print("\n🔧 Generating fallbacks for tree mappings...")
    modified_count = 0

    for category_key in mappings:
        if category_key == "_metadata":
            continue

        category = mappings[category_key]
        if not isinstance(category, dict):
            continue

        for asset_type, asset_info in category.items():
            if not isinstance(asset_info, dict):
                continue

            # Check if this is a tree mapping with variety_pool
            if asset_info.get("category") == "nature" and "variety_pool" in asset_info:
                variety_pool = asset_info["variety_pool"]

                # Generate fallbacks
                fallbacks = generate_fallback_for_mapping(asset_info, map_trees, variety_pool)

                if fallbacks:
                    asset_info["fallbacks"] = fallbacks
                    print(f"  ✅ {asset_type}: {len(fallbacks)} fallbacks")
                    modified_count += 1

    # Save updated mappings
    print(f"\n💾 Saving updated mappings ({modified_count} trees updated)...")
    with open(mappings_path, "w") as f:
        json.dump(mappings, f, indent=2, ensure_ascii=False)

    print("\n✅ Fallback generation complete!")
    print(f"   Modified {modified_count} tree mappings")
    print("   Run portal_convert.py to test updated mappings")


if __name__ == "__main__":
    main()
