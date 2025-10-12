#!/usr/bin/env python3
"""Add missing Kursk spawners to asset catalog and mapping table."""

import json
from pathlib import Path

# Load missing spawners
missing_spawners_path = Path("asset_audit/MISSING_SPAWNERS.json")
with open(missing_spawners_path) as f:
    missing_data = json.load(f)

# Add to BF1942 asset catalog
catalog_path = Path("asset_audit/bf1942_asset_catalog.json")
with open(catalog_path) as f:
    catalog = json.load(f)

print(f"📖 Loaded BF1942 asset catalog: {len(catalog)} assets")

# Add catalog entries
added_to_catalog = 0
for asset_name, asset_data in missing_data["catalog_entries"].items():
    if asset_name not in catalog:
        catalog[asset_name] = asset_data
        added_to_catalog += 1
        print(f"  ✅ Added to catalog: {asset_name}")
    else:
        print(f"  ⏭️  Already in catalog: {asset_name}")

# Save updated catalog
with open(catalog_path, "w") as f:
    json.dump(catalog, f, indent=2)

print(f"\n✅ Updated catalog: +{added_to_catalog} assets (now {len(catalog)} total)")

# Add to BF1942→Portal mapping table
mappings_path = Path("asset_audit/bf1942_to_portal_mappings.json")
with open(mappings_path) as f:
    mappings = json.load(f)

print(f"\n📖 Loaded BF1942→Portal mappings")

# Find spawners section
if "spawners" not in mappings:
    mappings["spawners"] = {}
    print("  ℹ️  Created spawners section")

# Add mapping entries
added_to_mappings = 0
for asset_name, mapping_data in missing_data["mapping_entries"].items():
    if asset_name not in mappings["spawners"]:
        mappings["spawners"][asset_name] = mapping_data
        added_to_mappings += 1
        print(f"  ✅ Added mapping: {asset_name} → {mapping_data['portal_equivalent']}")
    else:
        print(f"  ⏭️  Already mapped: {asset_name}")

# Update metadata
if "_metadata" in mappings:
    mappings["_metadata"]["total_bf1942_assets"] = len(catalog)
    mappings["_metadata"]["last_updated"] = "2025-10-12"

# Save updated mappings
with open(mappings_path, "w") as f:
    json.dump(mappings, f, indent=2)

print(f"\n✅ Updated mappings: +{added_to_mappings} spawner mappings")
print(f"   Total spawners section: {len(mappings['spawners'])} entries")

print("\n" + "=" * 70)
print("✅ COMPLETE - Missing Kursk spawners added successfully")
print("=" * 70)
print(f"\nFiles updated:")
print(f"  • {catalog_path}")
print(f"  • {mappings_path}")
print(f"\nNext steps:")
print(f"  1. Run: python3 tools/complete_asset_analysis.py")
print(f"  2. Verify: Kursk asset coverage should be 100%")
print(f"  3. Commit changes with descriptive message")
