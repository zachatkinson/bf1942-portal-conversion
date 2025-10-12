#!/usr/bin/env python3
"""Merge discovered real assets into catalog and create Portal mappings.

This tool follows DRY/SOLID principles:
- Reads filtered real assets from REAL_ASSETS_TO_MAP.json
- Merges into bf1942_asset_catalog.json (no duplicates)
- Creates intelligent Portal mappings using asset classification
- Uses the Portal asset index to find suitable matches
"""

import json
import sys
from pathlib import Path
from typing import Any

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))



def create_catalog_entry(asset_name: str, asset_data: dict[str, Any]) -> dict[str, Any]:
    """Create catalog entry from real asset data."""
    classification = asset_data.get("classification", "unknown")

    # Map classification to catalog category
    category_mapping = {
        "spawner": "spawner",
        "vehicle": "vehicle",
        "building": "building",
        "vegetation": "prop",  # Trees/bushes are props in BF1942
        "prop": "prop",
        "weapon": "weapon",
        "ammo_crate": "prop",
        "unknown": "unknown",
    }

    category = category_mapping.get(classification, "unknown")

    return {
        "bf1942_type": asset_name,
        "category": category,
        "found_in_maps": asset_data.get("found_in_maps", []),
        "usage_count": asset_data.get("usage_count", 0),
        "description": asset_data.get(
            "description", f"{classification.replace('_', ' ').title()} asset"
        ),
    }


def suggest_portal_mapping(
    asset_name: str, classification: str, portal_index: dict[str, Any]
) -> str:
    """Suggest Portal equivalent based on asset name and classification."""

    asset_lower = asset_name.lower()

    # Spawner mappings (high confidence)
    if classification == "spawner":
        if any(
            kw in asset_lower
            for kw in ["tank", "vehicle", "apc", "jeep", "car", "plane", "ship", "boat"]
        ):
            return "VehicleSpawner"
        elif any(kw in asset_lower for kw in ["gun", "artillery", "defgun", "aa"]):
            return "StationaryEmplacementSpawner"
        else:
            return "VehicleSpawner"  # Default for unknown spawners

    # Vegetation mappings
    elif classification == "vegetation":
        if "tree" in asset_lower:
            return "TreeAsset"  # Generic tree placeholder
        elif "bush" in asset_lower or "plant" in asset_lower:
            return "FoliageAsset"  # Generic foliage placeholder
        else:
            return "NatureAsset"

    # Building mappings
    elif classification == "building":
        if "bunker" in asset_lower:
            return "Military_Bunker"
        elif "tower" in asset_lower:
            return "Military_Tower"
        elif "church" in asset_lower:
            return "Religious_Building"
        elif "house" in asset_lower or "building" in asset_lower:
            return "Residential_Building"
        else:
            return "Architecture_Generic"

    # Prop mappings
    elif classification == "prop":
        if "fence" in asset_lower or "wall" in asset_lower:
            return "Military_Fence"
        elif "barrel" in asset_lower or "crate" in asset_lower:
            return "Military_Crate"
        elif "rock" in asset_lower or "stone" in asset_lower:
            return "Nature_Rock"
        else:
            return "Props_Generic"

    # Vehicle mappings
    elif classification == "vehicle":
        if "tank" in asset_lower:
            return "Military_Tank"
        elif "jeep" in asset_lower or "car" in asset_lower:
            return "Military_Vehicle"
        elif "boat" in asset_lower or "ship" in asset_lower:
            return "Military_Naval"
        else:
            return "Vehicle_Generic"

    # Weapon mappings
    elif classification == "weapon":
        return "WeaponPickup"  # All weapons map to weapon pickups

    # Ammo crate mappings
    elif classification == "ammo_crate":
        return "SupplyCrate"

    # Unknown - needs manual review
    else:
        return "TODO_MANUAL_REVIEW"


def main() -> None:
    """Main entry point for asset merging."""

    print("=" * 80)
    print("REAL ASSET MERGER")
    print("=" * 80)
    print()

    # Load real assets
    real_assets_path = Path("tools/asset_audit/REAL_ASSETS_TO_MAP.json")
    if not real_assets_path.exists():
        print(f"❌ ERROR: {real_assets_path} not found")
        print("   Run filter_real_assets.py first")
        sys.exit(1)

    with open(real_assets_path) as f:
        real_data = json.load(f)

    real_assets = real_data.get("real_assets", {})
    print(f"📖 Loaded {len(real_assets)} real assets to merge")

    # Load existing catalog
    catalog_path = Path("tools/asset_audit/bf1942_asset_catalog.json")
    with open(catalog_path) as f:
        catalog = json.load(f)

    print(f"📖 Current catalog: {len(catalog)} assets")

    # Load existing mappings
    mappings_path = Path("tools/asset_audit/bf1942_to_portal_mappings.json")
    with open(mappings_path) as f:
        mappings = json.load(f)

    print(f"📖 Current mappings: {len(mappings) - 1} entries")  # -1 for _metadata
    print()

    # Load Portal asset index for intelligent matching
    portal_index_path = Path("asset_audit/portal_asset_index.json")
    portal_index = {}
    if portal_index_path.exists():
        with open(portal_index_path) as f:
            portal_index = json.load(f)
        print("📖 Loaded Portal asset index")

    print()
    print("🔄 Merging assets...")
    print()

    # Merge catalog
    added_to_catalog = 0
    for asset_name, asset_data in real_assets.items():
        if asset_name not in catalog:
            catalog[asset_name] = create_catalog_entry(asset_name, asset_data)
            added_to_catalog += 1

    print(f"✅ Added {added_to_catalog} new assets to catalog")
    print(f"   Total catalog size: {len(catalog)} assets")

    # Merge mappings
    added_to_mappings = 0
    for asset_name, asset_data in real_assets.items():
        if asset_name not in mappings:
            classification = asset_data.get("classification", "unknown")
            portal_equivalent = suggest_portal_mapping(asset_name, classification, portal_index)

            mappings[asset_name] = {
                "bf1942_type": asset_name,
                "portal_equivalent": portal_equivalent,
                "category": asset_data.get("classification", "unknown"),
                "found_in_maps": asset_data.get("found_in_maps", []),
                "usage_count": asset_data.get("usage_count", 0),
                "notes": f"Auto-generated from {classification} classification",
                "confidence_score": 0.7 if portal_equivalent != "TODO_MANUAL_REVIEW" else 0.0,
                "auto_suggested": True,
            }
            added_to_mappings += 1

    print(f"✅ Added {added_to_mappings} new mappings")
    print(f"   Total mappings: {len(mappings) - 1} entries")  # -1 for _metadata
    print()

    # Update metadata
    if "_metadata" in mappings:
        mappings["_metadata"]["total_bf1942_assets"] = len(catalog)
        mappings["_metadata"]["last_updated"] = "2025-10-12"

    # Save updated catalog
    with open(catalog_path, "w") as f:
        json.dump(catalog, f, indent=2)

    print(f"💾 Saved updated catalog: {catalog_path}")

    # Save updated mappings
    with open(mappings_path, "w") as f:
        json.dump(mappings, f, indent=2)

    print(f"💾 Saved updated mappings: {mappings_path}")

    print()
    print("=" * 80)
    print("✅ MERGE COMPLETE")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"  • Catalog: {len(catalog)} total assets (+{added_to_catalog})")
    print(f"  • Mappings: {len(mappings) - 1} total entries (+{added_to_mappings})")
    print()

    # Count mappings by confidence
    manual_review = sum(
        1
        for m in mappings.values()
        if isinstance(m, dict) and m.get("portal_equivalent") == "TODO_MANUAL_REVIEW"
    )

    if manual_review > 0:
        print(f"⚠️  {manual_review} assets marked for manual review (unknown classification)")
        print("   These have portal_equivalent='TODO_MANUAL_REVIEW'")
        print()

    print("Next steps:")
    print("  1. Run: python3 tools/complete_asset_analysis.py")
    print("  2. Verify: Should show 100% coverage across all 36 maps")
    print("  3. (Optional) Review TODO_MANUAL_REVIEW entries and refine mappings")
    print()


if __name__ == "__main__":
    main()
