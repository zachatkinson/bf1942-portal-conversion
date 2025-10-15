#!/usr/bin/env python3
"""Comprehensive asset scanner for ALL extracted BF1942 maps.

Scans base game + XPack1 (Road to Rome) + XPack2 (Secret Weapons) and discovers
every unique asset type across all 36 maps.
"""

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from bfportal.generators.constants.paths import (
    DIR_BF1942_EXTRACTED_BASE,
    DIR_BF1942_EXTRACTED_XPACK1,
    DIR_BF1942_EXTRACTED_XPACK2,
    get_project_root,
)

# BF1942 map locations
MAP_ROOTS = [
    get_project_root() / DIR_BF1942_EXTRACTED_BASE,  # Base game (21 maps)
    get_project_root() / DIR_BF1942_EXTRACTED_XPACK1,  # Road to Rome (6 maps)
    get_project_root() / DIR_BF1942_EXTRACTED_XPACK2,  # Secret Weapons (9 maps)
]


def scan_con_file(con_path: Path) -> set[str]:
    """Extract asset type names from .con file."""
    asset_types = set()

    try:
        with open(con_path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()

                # Static objects: Object.create <AssetType>
                if line.startswith(
                    ("Object.create", "ObjectTemplate.create", "ObjectSpawnTemplate.create")
                ):
                    parts = line.split()
                    if len(parts) >= 2:
                        asset_types.add(parts[1])

    except Exception as e:
        print(f"  ⚠️  Error reading {con_path}: {e}")

    return asset_types


def scan_map_directory(map_dir: Path) -> dict[str, Any]:
    """Scan a single map directory for all asset types."""
    asset_types: set[str] = set()
    files_scanned = 0

    # Scan all .con files in the map directory
    for con_file in map_dir.rglob("*.con"):
        files_scanned += 1
        asset_types.update(scan_con_file(con_file))

    return {
        "name": map_dir.name,
        "asset_types": sorted(asset_types),
        "unique_count": len(asset_types),
        "files_scanned": files_scanned,
    }


def main() -> None:
    print("=" * 80)
    print("COMPREHENSIVE BF1942 ASSET DISCOVERY")
    print("=" * 80)
    print()

    # Discover all maps
    all_maps: list[Path] = []
    for root in MAP_ROOTS:
        if root.exists():
            all_maps.extend([d for d in root.iterdir() if d.is_dir()])

    print(f"📂 Found {len(all_maps)} extracted maps:")
    for i, map_dir in enumerate(all_maps, 1):
        print(f"  {i:2d}. {map_dir.name}")
    print()

    # Scan all maps
    print("🔍 Scanning all maps for asset types...")
    print()

    map_data: list[dict[str, Any]] = []
    all_discovered_assets: set[str] = set()
    asset_usage: dict[str, list[str]] = defaultdict(list)

    for map_dir in all_maps:
        print(f"  📖 Scanning: {map_dir.name}...")
        data = scan_map_directory(map_dir)
        map_data.append(data)

        # Track global asset usage
        for asset_type in data["asset_types"]:
            all_discovered_assets.add(asset_type)
            asset_usage[asset_type].append(map_dir.name)

        print(f"     Found {data['unique_count']} unique assets in {data['files_scanned']} files")

    print()
    print("=" * 80)
    print("DISCOVERY SUMMARY")
    print("=" * 80)
    print(f"Total maps scanned: {len(map_data)}")
    print(f"Total unique asset types discovered: {len(all_discovered_assets)}")
    print()

    # Load current catalog
    catalog_path = get_project_root() / "tools" / "asset_audit" / "bf1942_asset_catalog.json"
    with open(catalog_path) as f:
        catalog = json.load(f)

    print(f"📖 Current catalog: {len(catalog)} assets")
    print()

    # Find missing assets
    catalog_assets = set(catalog.keys())
    missing_assets = all_discovered_assets - catalog_assets

    if missing_assets:
        print(f"❌ MISSING ASSETS: {len(missing_assets)} assets NOT in catalog")
        print()

        # Create missing asset entries
        missing_entries: dict[str, dict[str, Any]] = {}
        for asset_type in sorted(missing_assets):
            maps_using = asset_usage[asset_type]
            missing_entries[asset_type] = {
                "bf1942_type": asset_type,
                "category": "unknown",
                "found_in_maps": sorted(maps_using),
                "usage_count": len(maps_using),
                "description": f"Asset discovered in {len(maps_using)} map(s)",
            }
            print(
                f"  • {asset_type} (used in {len(maps_using)} maps: {', '.join(maps_using[:3])}{'...' if len(maps_using) > 3 else ''})"
            )

        # Save missing assets to JSON
        missing_path = get_project_root() / "tools" / "asset_audit" / "MISSING_ASSETS_ALL_MAPS.json"
        with open(missing_path, "w") as f:
            json.dump(
                {
                    "_metadata": {
                        "description": "Missing assets discovered across all 36 BF1942 maps",
                        "total_maps_scanned": len(map_data),
                        "total_missing": len(missing_assets),
                        "scan_date": "2025-10-12",
                    },
                    "missing_assets": missing_entries,
                },
                f,
                indent=2,
            )

        print()
        print(f"💾 Saved missing assets to: {missing_path}")
    else:
        print("✅ All discovered assets are in catalog!")

    print()

    # Asset usage statistics
    print("=" * 80)
    print("TOP 20 MOST COMMON ASSETS")
    print("=" * 80)

    sorted_by_usage = sorted(asset_usage.items(), key=lambda x: len(x[1]), reverse=True)
    for i, (asset_type, maps) in enumerate(sorted_by_usage[:20], 1):
        print(f"{i:2d}. {asset_type:40s} ({len(maps):2d} maps)")

    print()

    # Save complete scan results
    results_path = get_project_root() / "tools" / "asset_audit" / "COMPLETE_ASSET_SCAN.json"
    with open(results_path, "w") as f:
        json.dump(
            {
                "_metadata": {
                    "description": "Complete asset scan across all BF1942 maps",
                    "total_maps": len(map_data),
                    "total_unique_assets": len(all_discovered_assets),
                    "catalog_size": len(catalog),
                    "missing_count": len(missing_assets),
                    "scan_date": "2025-10-12",
                },
                "maps": map_data,
                "asset_usage": {k: sorted(v) for k, v in asset_usage.items()},
            },
            f,
            indent=2,
        )

    print(f"💾 Saved complete scan results to: {results_path}")
    print()
    print("=" * 80)
    print("✅ SCAN COMPLETE")
    print("=" * 80)

    if missing_assets:
        print()
        print("Next steps:")
        print("  1. Review: asset_audit/MISSING_ASSETS_ALL_MAPS.json")
        print("  2. Add to catalog: merge missing_assets into bf1942_asset_catalog.json")
        print("  3. Create mappings: add Portal equivalents to bf1942_to_portal_mappings.json")
        print("  4. Re-run verification to confirm 100% coverage")


if __name__ == "__main__":
    main()
