#!/usr/bin/env python3
"""Portal Asset Catalog Analyzer.

Analyzes the Portal asset catalog to understand what assets are available
for mapping BF1942 assets.

Usage:
    python3 tools/analyze_portal_assets.py
"""

import json
from collections import defaultdict
from pathlib import Path


def analyze_portal_assets(asset_types_path: Path) -> None:
    """Analyze Portal asset catalog."""
    with open(asset_types_path) as f:
        data = json.load(f)

    assets = data.get("AssetTypes", [])
    print("=" * 70)
    print("Portal Asset Catalog Analysis")
    print("=" * 70)
    print(f"\nTotal Portal assets: {len(assets)}")

    # Categorize by directory
    categories = defaultdict(int)
    by_category = defaultdict(list)

    for asset in assets:
        dir_path = asset.get("directory", "Unknown")
        cat = dir_path.split("/")[0] if "/" in dir_path else dir_path
        categories[cat] += 1
        by_category[cat].append(asset["type"])

    print("\n" + "-" * 70)
    print("Assets by top-level category:")
    print("-" * 70)
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {cat:30s} {count:4d} assets")

    # Find gameplay-related assets
    print("\n" + "-" * 70)
    print("Gameplay Assets (for HQs, spawners, capture points):")
    print("-" * 70)
    gameplay = [a for a in assets if "Gameplay" in a.get("directory", "")]
    for asset in sorted(gameplay, key=lambda x: x["type"]):
        print(f"  {asset['type']:40s} → {asset['directory']}")

    # Find vehicle assets
    print("\n" + "-" * 70)
    print("Vehicle Assets:")
    print("-" * 70)
    vehicles = [
        a
        for a in assets
        if "vehicle" in a["type"].lower()
        or "tank" in a["type"].lower()
        or "jeep" in a["type"].lower()
        or "boat" in a["type"].lower()
        or "plane" in a["type"].lower()
        or "aircraft" in a["type"].lower()
    ]

    for asset in sorted(vehicles, key=lambda x: x["type"])[:30]:  # Show first 30
        restrictions = asset.get("levelRestrictions", [])
        if restrictions:
            print(f"  {asset['type']:40s} (restricted to {len(restrictions)} maps)")
        else:
            print(f"  {asset['type']:40s} (no restrictions)")

    if len(vehicles) > 30:
        print(f"  ... and {len(vehicles) - 30} more vehicle assets")

    # Find building/structure assets
    print("\n" + "-" * 70)
    print("Architecture/Building Assets (sample):")
    print("-" * 70)
    buildings = [a for a in assets if "Architecture" in a.get("directory", "")]
    for asset in sorted(buildings, key=lambda x: x["type"])[:20]:
        restrictions = asset.get("levelRestrictions", [])
        if restrictions:
            print(f"  {asset['type']:40s} (restricted to {len(restrictions)} maps)")
        else:
            print(f"  {asset['type']:40s} (no restrictions)")

    if len(buildings) > 20:
        print(f"  ... and {len(buildings) - 20} more building assets")

    # Show unrestricted assets (can be used on any map)
    unrestricted = [a for a in assets if not a.get("levelRestrictions", [])]
    print("\n" + "-" * 70)
    print(f"Unrestricted Assets (usable on any map): {len(unrestricted)}")
    print("-" * 70)

    # Show most restricted assets
    restricted_counts = defaultdict(list)
    for asset in assets:
        restrictions = asset.get("levelRestrictions", [])
        if restrictions:
            restricted_counts[len(restrictions)].append(asset["type"])

    print("\n" + "-" * 70)
    print("Asset Restriction Statistics:")
    print("-" * 70)
    print(f"  Unrestricted (any map): {len(unrestricted)} assets")
    for count in sorted(restricted_counts.keys()):
        print(f"  Restricted to {count} map(s): {len(restricted_counts[count])} assets")


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    asset_types_path = project_root / "FbExportData" / "asset_types.json"

    if not asset_types_path.exists():
        print(f"❌ ERROR: Asset types file not found: {asset_types_path}")
        return 1

    analyze_portal_assets(asset_types_path)

    return 0


if __name__ == "__main__":
    exit(main())
