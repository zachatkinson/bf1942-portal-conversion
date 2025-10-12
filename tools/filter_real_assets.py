#!/usr/bin/env python3
"""Filter real assets from map scan results using intelligent classification.

This tool uses the asset classification system to distinguish between:
- Real assets (vehicles, buildings, vegetation, weapons) → Need Portal mappings
- Metadata (spawn points, control point names) → Don't need mappings
"""

import json
import sys
from pathlib import Path

# Add tools directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from bfportal.classifiers import CompositeAssetClassifier


def main() -> None:
    """Main entry point for asset filtering."""

    print("=" * 80)
    print("REAL ASSET FILTER")
    print("=" * 80)
    print()

    # Load missing assets from scan
    missing_path = Path("tools/asset_audit/MISSING_ASSETS_ALL_MAPS.json")
    if not missing_path.exists():
        print(f"❌ ERROR: {missing_path} not found")
        print("   Run scan_all_maps.py first to generate missing assets report")
        sys.exit(1)

    with open(missing_path) as f:
        data = json.load(f)

    missing_assets = data.get("missing_assets", {})
    print(f"📖 Loaded {len(missing_assets)} missing assets from scan")
    print()

    # Classify all assets
    print("🔍 Classifying assets...")
    classifier = CompositeAssetClassifier()

    classifications = classifier.classify_many(list(missing_assets.keys()))

    # Get statistics
    stats = classifier.get_statistics(list(missing_assets.keys()))

    print()
    print("=" * 80)
    print("CLASSIFICATION RESULTS")
    print("=" * 80)
    print()
    print(f"Total assets analyzed: {stats['_total']}")
    print(f"Real assets (need Portal mappings): {stats['_total_real_assets']}")
    print(f"Metadata (spawn points, etc.): {stats['_total_metadata']}")
    print()

    # Breakdown by category
    print("Breakdown by category:")
    for category, count in sorted(stats.items()):
        if not category.startswith("_"):
            print(f"  • {category}: {count}")

    print()

    # Filter real assets only
    real_assets = {
        name: {
            **asset_data,
            "classification": classifications[name].category,
            "classification_reason": classifications[name].reason,
        }
        for name, asset_data in missing_assets.items()
        if classifications[name].is_real_asset
    }

    print("=" * 80)
    print(f"REAL ASSETS: {len(real_assets)} assets need Portal mappings")
    print("=" * 80)
    print()

    # Show by category
    by_category: dict[str, list[str]] = {}
    for name, data in real_assets.items():
        cat = data["classification"]
        by_category.setdefault(cat, []).append(name)

    for category in sorted(by_category.keys()):
        assets_in_cat = by_category[category]
        print(f"### {category.title()} ({len(assets_in_cat)} assets)")
        for asset_name in sorted(assets_in_cat)[:20]:  # Show first 20
            print(f"  • {asset_name}")
        if len(assets_in_cat) > 20:
            print(f"  ... and {len(assets_in_cat) - 20} more")
        print()

    # Save filtered real assets
    output_path = Path("tools/asset_audit/REAL_ASSETS_TO_MAP.json")
    with open(output_path, "w") as f:
        json.dump(
            {
                "_metadata": {
                    "description": "Real BF1942 assets that need Portal mappings",
                    "total_scanned": len(missing_assets),
                    "real_assets": len(real_assets),
                    "metadata_filtered": len(missing_assets) - len(real_assets),
                    "scan_date": data.get("_metadata", {}).get("scan_date", "2025-10-12"),
                },
                "real_assets": real_assets,
                "classification_stats": {k: v for k, v in stats.items() if not k.startswith("_")},
            },
            f,
            indent=2,
        )

    print("💾 Saved filtered real assets to:", output_path)
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"  Scanned: {len(missing_assets)} missing assets")
    print(f"  Real assets: {len(real_assets)} need Portal mappings")
    print(
        f"  Metadata: {len(missing_assets) - len(real_assets)} spawn points/control points (filtered out)"
    )
    print()
    print("Next steps:")
    print("  1. Review: tools/asset_audit/REAL_ASSETS_TO_MAP.json")
    print("  2. Add to catalog: Merge real assets into bf1942_asset_catalog.json")
    print("  3. Create mappings: Add Portal equivalents to bf1942_to_portal_mappings.json")
    print()


if __name__ == "__main__":
    main()
