#!/usr/bin/env python3
"""BF6 Portal Asset Analyzer.

This tool parses asset_types.json to catalog and categorize all available
BF6 Portal assets for the map conversion project.

Usage:
    python tools/analyze_bf6_assets.py

Output:
    - .claude/BF6_Asset_Catalog.md - Comprehensive asset reference
    - tools/bf6_assets_by_category.json - Categorized asset database
"""

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List


def load_asset_types(json_path: str) -> List[Dict]:
    """Load and parse asset_types.json.

    Args:
        json_path: Path to asset_types.json

    Returns:
        List of asset type dictionaries

    Raises:
        FileNotFoundError: If json file doesn't exist
        json.JSONDecodeError: If JSON is malformed
    """
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    return data.get("AssetTypes", [])


def categorize_assets(assets: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize assets by directory and type.

    Args:
        assets: List of asset dictionaries

    Returns:
        Dictionary mapping categories to asset lists
    """
    categories = defaultdict(list)

    for asset in assets:
        asset_type = asset.get("type", "Unknown")
        directory = asset.get("directory", "Uncategorized")
        level_restrictions = asset.get("levelRestrictions", [])

        # Extract category from directory path
        if "/" in directory:
            main_category = directory.split("/")[0]
        else:
            main_category = directory

        # Store asset with useful metadata
        asset_info = {
            "type": asset_type,
            "directory": directory,
            "category": main_category,
            "restricted": len(level_restrictions) > 0,
            "available_on": level_restrictions if level_restrictions else ["ALL"],
            "constants": asset.get("constants", []),
            "properties": asset.get("properties", []),
        }

        categories[main_category].append(asset_info)

    return dict(categories)


def find_vehicle_spawners(assets: List[Dict]) -> List[Dict]:
    """Find all vehicle spawner assets.

    Args:
        assets: List of asset dictionaries

    Returns:
        List of vehicle spawner assets
    """
    spawners = []
    keywords = ["spawner", "spawn", "vehicle"]

    for asset in assets:
        asset_type = asset.get("type", "").lower()
        directory = asset.get("directory", "").lower()

        # Check if this is a spawner
        if any(keyword in asset_type for keyword in keywords) or "vehicle" in directory or "spawner" in directory:
            spawners.append(asset)

    return spawners


def find_terrain_assets(assets: List[Dict]) -> List[Dict]:
    """Find terrain and landscape assets.

    Args:
        assets: List of asset dictionaries

    Returns:
        List of terrain assets
    """
    terrain = []
    keywords = ["terrain", "landscape", "ground", "heightmap"]

    for asset in assets:
        asset_type = asset.get("type", "").lower()
        directory = asset.get("directory", "").lower()

        if any(keyword in asset_type for keyword in keywords) or any(keyword in directory for keyword in keywords):
            terrain.append(asset)

    return terrain


def find_gameplay_objects(assets: List[Dict]) -> List[Dict]:
    """Find gameplay-related objects (HQs, spawners, capture points).

    Args:
        assets: List of asset dictionaries

    Returns:
        List of gameplay assets
    """
    gameplay = []
    keywords = [
        "hq",
        "headquarters",
        "spawner",
        "spawnpoint",
        "capturepoint",
        "capture",
        "objective",
        "combatarea",
        "areaTrigger",
        "trigger",
    ]

    for asset in assets:
        asset_type = asset.get("type", "").lower()
        directory = asset.get("directory", "").lower()

        if any(keyword in asset_type for keyword in keywords) or "gameplay" in directory:
            gameplay.append(asset)

    return gameplay


def find_unrestricted_assets(assets: List[Dict]) -> List[Dict]:
    """Find assets with no level restrictions (usable on any map).

    Args:
        assets: List of asset dictionaries

    Returns:
        List of unrestricted assets
    """
    unrestricted = []

    for asset in assets:
        level_restrictions = asset.get("levelRestrictions", [])
        if not level_restrictions:
            unrestricted.append(asset)

    return unrestricted


def analyze_level_restrictions(assets: List[Dict]) -> Dict[str, int]:
    """Analyze how many assets are restricted to specific levels.

    Args:
        assets: List of asset dictionaries

    Returns:
        Dictionary mapping level names to asset counts
    """
    level_counts = defaultdict(int)

    for asset in assets:
        level_restrictions = asset.get("levelRestrictions", [])
        if level_restrictions:
            for level in level_restrictions:
                level_counts[level] += 1

    return dict(sorted(level_counts.items(), key=lambda x: x[1], reverse=True))


def generate_statistics(assets: List[Dict]) -> Dict:
    """Generate overall statistics about the asset library.

    Args:
        assets: List of asset dictionaries

    Returns:
        Dictionary of statistics
    """
    total_assets = len(assets)

    # Count by restriction status
    unrestricted = len([a for a in assets if not a.get("levelRestrictions", [])])
    restricted = total_assets - unrestricted

    # Count by category
    categories = set()
    for asset in assets:
        directory = asset.get("directory", "")
        if "/" in directory:
            categories.add(directory.split("/")[0])
        else:
            categories.add(directory)

    return {
        "total_assets": total_assets,
        "unrestricted_assets": unrestricted,
        "restricted_assets": restricted,
        "restriction_percentage": round((restricted / total_assets) * 100, 2),
        "unique_categories": len(categories),
        "category_names": sorted(categories),
    }


def main():
    """Main entry point."""
    # Paths
    project_root = Path(__file__).parent.parent
    asset_json_path = project_root / "FbExportData" / "asset_types.json"

    if not asset_json_path.exists():
        print(f"ERROR: {asset_json_path} not found")
        sys.exit(1)

    print("Loading asset_types.json...")
    assets = load_asset_types(str(asset_json_path))
    print(f"Loaded {len(assets)} assets")

    print("\nCategorizing assets...")
    categorized = categorize_assets(assets)
    print(f"Found {len(categorized)} categories")

    print("\nFinding vehicle spawners...")
    vehicle_spawners = find_vehicle_spawners(assets)
    print(f"Found {len(vehicle_spawners)} vehicle spawners")

    print("\nFinding terrain assets...")
    terrain_assets = find_terrain_assets(assets)
    print(f"Found {len(terrain_assets)} terrain assets")

    print("\nFinding gameplay objects...")
    gameplay_objects = find_gameplay_objects(assets)
    print(f"Found {len(gameplay_objects)} gameplay objects")

    print("\nFinding unrestricted assets...")
    unrestricted = find_unrestricted_assets(assets)
    print(f"Found {len(unrestricted)} unrestricted assets")

    print("\nAnalyzing level restrictions...")
    level_restrictions = analyze_level_restrictions(assets)
    print(f"Assets restricted across {len(level_restrictions)} levels")

    print("\nGenerating statistics...")
    stats = generate_statistics(assets)

    # Print summary
    print("\n" + "=" * 70)
    print("BF6 PORTAL ASSET SUMMARY")
    print("=" * 70)
    print(f"Total Assets:           {stats['total_assets']:,}")
    print(
        f"Unrestricted:           {stats['unrestricted_assets']:,} ({100 - stats['restriction_percentage']:.1f}%)"
    )
    print(
        f"Restricted:             {stats['restricted_assets']:,} ({stats['restriction_percentage']:.1f}%)"
    )
    print(f"Categories:             {stats['unique_categories']}")
    print()
    print("Top 10 Categories:")
    for i, (cat, assets_list) in enumerate(
        sorted(categorized.items(), key=lambda x: len(x[1]), reverse=True)[:10], 1
    ):
        print(f"  {i:2}. {cat:30} {len(assets_list):5,} assets")
    print("=" * 70)

    # Save categorized data
    output_path = project_root / "tools" / "bf6_assets_by_category.json"
    output_data = {
        "statistics": stats,
        "categories": {cat: len(assets_list) for cat, assets_list in categorized.items()},
        "vehicle_spawners": [v["type"] for v in vehicle_spawners],
        "terrain_assets": [t["type"] for t in terrain_assets],
        "gameplay_objects": [g["type"] for g in gameplay_objects],
        "unrestricted_count": len(unrestricted),
        "level_restrictions": level_restrictions,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print(f"\nSaved analysis to: {output_path}")
    print("\nNext: Run detailed analysis for Kursk-specific assets")


if __name__ == "__main__":
    main()
