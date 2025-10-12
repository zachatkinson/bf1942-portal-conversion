#!/usr/bin/env python3
"""BF1942 Complete Asset Audit Tool.

Scans ALL BF1942 maps (base + XPacks) and catalogs every unique asset type.
This creates a comprehensive database for mapping to BF6 Portal equivalents.

Usage:
    python3 tools/audit_bf1942_assets.py

Output:
    - bf1942_asset_catalog.json: Complete list of all unique assets
    - bf1942_asset_statistics.json: Usage statistics per asset
    - bf1942_to_portal_mappings.json: Template for Portal mappings
"""

import json
import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List


@dataclass
class AssetInfo:
    """Information about a BF1942 asset."""

    asset_type: str
    category: str  # vehicle, static, building, prop, weapon, kit
    found_in_maps: List[str]
    usage_count: int
    expansion: str  # base, xpack1, xpack2
    sample_properties: Dict  # Example properties from .con files


class BF1942AssetAuditor:
    """Audits all BF1942 maps for asset usage."""

    def __init__(self, bf1942_root: Path):
        self.bf1942_root = bf1942_root
        self.assets: Dict[str, AssetInfo] = {}
        self.asset_categories = {
            "vehicle": ["tank", "plane", "ship", "car", "boat", "helicopter", "apc"],
            "weapon": ["gun", "rifle", "pistol", "grenade", "mine", "knife"],
            "building": ["house", "bunker", "tower", "barracks", "factory", "church"],
            "prop": ["tree", "rock", "fence", "barrel", "crate", "debris"],
            "spawner": ["spawner", "spawnpoint", "controlpoint"],
            "kit": ["kit", "medic", "engineer", "assault", "scout", "antitank"],
        }

    def categorize_asset(self, asset_type: str) -> str:
        """Determine asset category from type name."""
        asset_lower = asset_type.lower()

        for category, keywords in self.asset_categories.items():
            for keyword in keywords:
                if keyword in asset_lower:
                    return category

        return "unknown"

    def parse_con_file(self, con_file: Path, map_name: str, expansion: str) -> None:
        """Parse .con file and extract asset references."""
        try:
            with open(con_file, encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            print(f"⚠️  Error reading {con_file}: {e}")
            return

        # Common patterns in .con files
        patterns = [
            # ObjectTemplate.create <type> <name>
            r"ObjectTemplate\.create\s+(\w+)\s+(\w+)",
            # ObjectTemplate.addTemplate <name>
            r"ObjectTemplate\.addTemplate\s+(\w+)",
            # run <path>/<name>.con
            r"run\s+.*?/(\w+)\.con",
            # GeometryTemplate.file <name>
            r"GeometryTemplate\.file\s+(\w+)",
            # ObjectTemplate.setNetworkableInfo <type>
            r"ObjectTemplate\.setNetworkableInfo\s+(\w+)",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    asset_type = match[0] if len(match) > 0 else match
                else:
                    asset_type = match

                # Skip common non-asset keywords
                skip_words = ["if", "else", "rem", "begin", "end", "var", "set"]
                if asset_type.lower() in skip_words:
                    continue

                # Add or update asset
                if asset_type not in self.assets:
                    category = self.categorize_asset(asset_type)
                    self.assets[asset_type] = AssetInfo(
                        asset_type=asset_type,
                        category=category,
                        found_in_maps=[map_name],
                        usage_count=1,
                        expansion=expansion,
                        sample_properties={},
                    )
                else:
                    if map_name not in self.assets[asset_type].found_in_maps:
                        self.assets[asset_type].found_in_maps.append(map_name)
                    self.assets[asset_type].usage_count += 1

    def scan_map(self, map_path: Path, map_name: str, expansion: str) -> None:
        """Scan a single map directory for assets."""
        print(f"  📁 Scanning {map_name} ({expansion})...")

        # Find all .con files recursively
        con_files = list(map_path.rglob("*.con"))

        if not con_files:
            print(f"    ⚠️  No .con files found in {map_path}")
            return

        print(f"    Found {len(con_files)} .con files")

        for con_file in con_files:
            self.parse_con_file(con_file, map_name, expansion)

    def scan_all_maps(self) -> None:
        """Scan all BF1942 maps (base + expansions)."""
        print("=" * 70)
        print("BF1942 Complete Asset Audit")
        print("=" * 70)

        # Base BF1942 maps
        base_maps_dir = self.bf1942_root / "extracted" / "Bf1942" / "Archives" / "bf1942" / "Levels"
        if base_maps_dir.exists():
            print("\n🎮 Scanning Base BF1942 Maps...")
            for map_dir in sorted(base_maps_dir.iterdir()):
                if map_dir.is_dir():
                    self.scan_map(map_dir, map_dir.name, "base")

        # XPack1: Road to Rome
        xpack1_maps_dir = self.bf1942_root / "extracted" / "XPack1" / "Bf1942" / "Levels"
        if xpack1_maps_dir.exists():
            print("\n🏛️  Scanning Road to Rome Maps...")
            for map_dir in sorted(xpack1_maps_dir.iterdir()):
                if map_dir.is_dir():
                    self.scan_map(map_dir, map_dir.name, "xpack1_rtr")

        # XPack2: Secret Weapons
        xpack2_maps_dir = self.bf1942_root / "extracted" / "XPack2" / "bf1942" / "Levels"
        if xpack2_maps_dir.exists():
            print("\n🔬 Scanning Secret Weapons Maps...")
            for map_dir in sorted(xpack2_maps_dir.iterdir()):
                if map_dir.is_dir():
                    self.scan_map(map_dir, map_dir.name, "xpack2_sw")

    def generate_statistics(self) -> Dict:
        """Generate asset usage statistics."""
        stats = {
            "total_unique_assets": len(self.assets),
            "by_category": defaultdict(int),
            "by_expansion": defaultdict(int),
            "most_used_assets": [],
            "expansion_exclusive_assets": {"base": [], "xpack1_rtr": [], "xpack2_sw": []},
        }

        # Category counts
        for asset in self.assets.values():
            stats["by_category"][asset.category] += 1
            stats["by_expansion"][asset.expansion] += 1

        # Most used assets
        sorted_assets = sorted(self.assets.values(), key=lambda x: x.usage_count, reverse=True)
        stats["most_used_assets"] = [
            {"asset": a.asset_type, "usage_count": a.usage_count, "maps": len(a.found_in_maps)}
            for a in sorted_assets[:20]
        ]

        # Expansion-exclusive assets
        for asset in self.assets.values():
            stats["expansion_exclusive_assets"][asset.expansion].append(asset.asset_type)

        return dict(stats)

    def generate_portal_mapping_template(self) -> Dict:
        """Generate template for BF1942 → Portal mappings."""
        mappings = {
            "_metadata": {
                "description": "BF1942 to BF6 Portal Asset Mappings",
                "total_bf1942_assets": len(self.assets),
                "status": "TODO - Map each asset to Portal equivalent",
            },
            "vehicles": {},
            "static_objects": {},
            "buildings": {},
            "props": {},
            "weapons": {},
            "kits": {},
            "spawners": {},
            "unknown": {},
        }

        # Group by category
        for asset_type, info in sorted(self.assets.items()):
            category_key = info.category if info.category != "unknown" else "unknown"

            # Add plural 's' for category key if needed
            if category_key == "vehicle":
                category_key = "vehicles"
            elif category_key == "weapon":
                category_key = "weapons"
            elif category_key == "kit":
                category_key = "kits"
            elif category_key == "spawner":
                category_key = "spawners"
            elif category_key == "building":
                category_key = "buildings"
            elif category_key == "prop":
                category_key = "props"
            elif category_key in ["static", "unknown"]:
                category_key = "static_objects"

            mappings[category_key][asset_type] = {
                "bf1942_type": asset_type,
                "portal_equivalent": "TODO",  # To be filled manually
                "category": info.category,
                "found_in_maps": info.found_in_maps[:3],  # Sample maps
                "usage_count": info.usage_count,
                "notes": "",
            }

        return mappings

    def save_results(self, output_dir: Path) -> None:
        """Save audit results to JSON files."""
        output_dir.mkdir(exist_ok=True)

        # 1. Complete asset catalog
        catalog = {asset_type: asdict(info) for asset_type, info in sorted(self.assets.items())}
        catalog_path = output_dir / "bf1942_asset_catalog.json"
        with open(catalog_path, "w") as f:
            json.dump(catalog, f, indent=2)
        print(f"\n✅ Saved asset catalog: {catalog_path}")

        # 2. Statistics
        stats = self.generate_statistics()
        stats_path = output_dir / "bf1942_asset_statistics.json"
        with open(stats_path, "w") as f:
            json.dump(stats, f, indent=2)
        print(f"✅ Saved statistics: {stats_path}")

        # 3. Portal mapping template
        mappings = self.generate_portal_mapping_template()
        mappings_path = output_dir / "bf1942_to_portal_mappings_template.json"
        with open(mappings_path, "w") as f:
            json.dump(mappings, f, indent=2)
        print(f"✅ Saved mapping template: {mappings_path}")

        # Print summary
        print("\n" + "=" * 70)
        print("📊 Audit Summary")
        print("=" * 70)
        print(f"Total unique assets found: {stats['total_unique_assets']}")
        print("\nBy category:")
        for category, count in sorted(stats["by_category"].items()):
            print(f"  {category}: {count}")
        print("\nBy expansion:")
        for expansion, count in sorted(stats["by_expansion"].items()):
            print(f"  {expansion}: {count}")
        print("\n💡 Next steps:")
        print("  1. Review bf1942_to_portal_mappings_template.json")
        print("  2. Map each 'TODO' to actual Portal asset from asset_types.json")
        print("  3. Rename to bf1942_to_portal_mappings.json when complete")
        print("  4. Use in portal_convert.py for automatic asset mapping")


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    bf1942_root = project_root / "bf1942_source"
    output_dir = project_root / "tools" / "asset_audit"

    if not bf1942_root.exists():
        print(f"❌ ERROR: BF1942 source directory not found: {bf1942_root}")
        return 1

    auditor = BF1942AssetAuditor(bf1942_root)
    auditor.scan_all_maps()
    auditor.save_results(output_dir)

    return 0


if __name__ == "__main__":
    exit(main())
