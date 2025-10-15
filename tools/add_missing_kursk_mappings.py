#!/usr/bin/env python3
"""Add missing BF1942 asset mappings for Kursk.

DRY/SOLID: Single tool to batch-add missing mappings
"""

import json
from pathlib import Path


def main():
    project_root = Path(__file__).parent.parent
    mappings_path = project_root / "tools" / "asset_audit" / "bf1942_to_portal_mappings.json"

    print("📖 Loading mappings...")
    with open(mappings_path) as f:
        mappings = json.load(f)

    # Add missing tree mappings
    new_trees = {
        "EU_Spruce4_M1": {
            "bf1942_type": "EU_Spruce4_M1",
            "portal_equivalent": "Birch_01_M_D",
            "category": "nature",
            "notes": "Large spruce tree → Medium Birch variant D (MP_Tungsten compatible)",
            "manually_verified": True,
            "variety_pool": [
                "Birch_01_M_D",
                "Birch_01_L",
                "Birch_01_L_B",
                "Birch_01_L_C",
                "JuniperPencil_01_L",
                "JuniperPencil_01_M_A",
            ],
            "randomize": True,
        },
        "EU_pine2_M1": {
            "bf1942_type": "EU_pine2_M1",
            "portal_equivalent": "JuniperPencil_01_M_A",
            "category": "nature",
            "notes": "Pine tree → Juniper Pencil (coniferous, MP_Tungsten compatible)",
            "manually_verified": True,
            "variety_pool": [
                "JuniperPencil_01_M_A",
                "JuniperPencil_01_M_B",
                "JuniperPencil_01_M_C",
                "Birch_01_M_D",
                "Birch_01_L",
            ],
            "randomize": True,
        },
        "EU_pine5_M1": {
            "bf1942_type": "EU_pine5_M1",
            "portal_equivalent": "JuniperPencil_01_L",
            "category": "nature",
            "notes": "Large pine tree → Large Juniper Pencil (coniferous, MP_Tungsten compatible)",
            "manually_verified": True,
            "variety_pool": ["JuniperPencil_01_L", "Birch_01_L", "Birch_01_L_B", "Birch_01_L_C"],
            "randomize": True,
        },
        "EU_pine7_M1": {
            "bf1942_type": "EU_pine7_M1",
            "portal_equivalent": "Birch_01_L",
            "category": "nature",
            "notes": "Pine tree → Large Birch (MP_Tungsten compatible)",
            "manually_verified": True,
            "variety_pool": ["Birch_01_L", "Birch_01_L_B", "Birch_01_L_C", "JuniperPencil_01_L"],
            "randomize": True,
        },
    }

    # Add missing building mappings
    new_buildings = {
        "eu_lumbermill_m1": {
            "bf1942_type": "eu_lumbermill_m1",
            "portal_equivalent": "OutskirtsHouseMediumRoof_01",
            "category": "building",
            "notes": "European lumbermill → Medium rural house (closest available)",
            "confidence_score": 0.6,
        },
        "rh_Russian_Barn_main_m1": {
            "bf1942_type": "rh_Russian_Barn_main_m1",
            "portal_equivalent": "OutskirtsHouseMediumRoof_01",
            "category": "building",
            "notes": "Russian barn → Medium rural house (closest available)",
            "confidence_score": 0.6,
        },
        "French_Barn_Lrg_m1": {
            "bf1942_type": "French_Barn_Lrg_m1",
            "portal_equivalent": "OutskirtsHouseMediumRoof_01",
            "category": "building",
            "notes": "French barn → Medium rural house (closest available)",
            "confidence_score": 0.6,
        },
        "openbase_lumbermill_Cpoint": {
            "bf1942_type": "openbase_lumbermill_Cpoint",
            "portal_equivalent": "OutskirtsHouseMediumRoof_01",
            "category": "building",
            "notes": "Open lumbermill control point → Medium rural house",
            "confidence_score": 0.6,
        },
    }

    # Add missing prop mappings
    new_props = {
        "eu_cart_M1": {
            "bf1942_type": "eu_cart_M1",
            "portal_equivalent": "CartWoodSmall_01",
            "category": "prop",
            "notes": "European cart → Wooden cart (perfect match)",
            "confidence_score": 0.95,
        },
        "sandbagu_m1": {
            "bf1942_type": "sandbagu_m1",
            "portal_equivalent": "BulkBag_01",
            "category": "prop",
            "notes": "Sandbag upper → Bulk bag (similar defensive prop)",
            "confidence_score": 0.7,
        },
    }

    # Add to appropriate categories
    if "nature" not in mappings:
        mappings["nature"] = {}
    if "buildings" not in mappings:
        mappings["buildings"] = {}
    if "props" not in mappings:
        mappings["props"] = {}

    added_count = 0

    for asset_type, mapping in new_trees.items():
        if asset_type not in mappings["nature"]:
            mappings["nature"][asset_type] = mapping
            print(f"  ✅ Added tree: {asset_type}")
            added_count += 1

    for asset_type, mapping in new_buildings.items():
        if asset_type not in mappings["buildings"]:
            mappings["buildings"][asset_type] = mapping
            print(f"  ✅ Added building: {asset_type}")
            added_count += 1

    for asset_type, mapping in new_props.items():
        if asset_type not in mappings["props"]:
            mappings["props"][asset_type] = mapping
            print(f"  ✅ Added prop: {asset_type}")
            added_count += 1

    # Update metadata
    current_total = mappings["_metadata"].get("total_bf1942_assets", 0)
    mappings["_metadata"]["total_bf1942_assets"] = current_total + added_count
    mappings["_metadata"]["last_updated"] = "2025-10-15"
    mappings["_metadata"]["notes"] = f"Added {added_count} Kursk assets"

    # Save
    print(f"\n💾 Saving {added_count} new mappings...")
    with open(mappings_path, "w") as f:
        json.dump(mappings, f, indent=2, ensure_ascii=False)

    print("✅ Done! Run generate_tree_fallbacks.py next to add map-specific fallbacks")


if __name__ == "__main__":
    main()
